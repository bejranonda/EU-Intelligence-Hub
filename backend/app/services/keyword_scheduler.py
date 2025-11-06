"""Keyword search scheduling and throttling utilities."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, List, Optional, Sequence

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.models import Keyword, KeywordSearchQueue

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class SchedulingCandidate:
    keyword: Keyword
    next_scheduled_at: datetime
    priority: int


def calculate_next_run(base: datetime, cooldown_minutes: int) -> datetime:
    """Calculate next eligible run time with cooldown."""

    return base + timedelta(minutes=cooldown_minutes)


def load_eligible_keywords(
    db: Session, limit: Optional[int] = None
) -> List[SchedulingCandidate]:
    """Return keywords eligible for scheduling based on cooldown and priority."""

    now = datetime.utcnow()
    cooldown_minutes = settings.keyword_search_cooldown_minutes

    query = (
        db.query(Keyword)
        .filter(
            and_(
                Keyword.search_priority >= settings.keyword_scheduler_min_priority,
                func.coalesce(Keyword.next_search_after, datetime(1970, 1, 1)) <= now,
            )
        )
        .order_by(
            Keyword.search_priority.desc(),
            func.coalesce(Keyword.last_searched, datetime(1970, 1, 1)),
        )
    )

    if limit:
        query = query.limit(limit)

    results: List[SchedulingCandidate] = []

    for keyword in query.all():  # type: ignore[attr-defined]
        next_run = keyword.next_search_after or calculate_next_run(
            keyword.last_searched or now - timedelta(minutes=cooldown_minutes + 1),
            cooldown_minutes,
        )

        if next_run <= now:
            results.append(
                SchedulingCandidate(
                    keyword=keyword,
                    next_scheduled_at=now,
                    priority=keyword.search_priority or 0,
                )
            )

    return results


def queue_keywords(db: Session, candidates: Sequence[SchedulingCandidate]) -> int:
    """Insert scheduling candidates into queue respecting duplicates."""

    if not candidates:
        return 0

    inserted = 0
    for candidate in candidates:
        existing = (
            db.query(KeywordSearchQueue)
            .filter(
                KeywordSearchQueue.keyword_id == candidate.keyword.id,
                KeywordSearchQueue.status.in_(["pending", "running"]),
            )
            .first()
        )

        if existing:
            continue

        job = KeywordSearchQueue(
            keyword_id=candidate.keyword.id,
            scheduled_at=candidate.next_scheduled_at,
            priority=candidate.priority,
            status="pending",
        )
        db.add(job)
        candidate.keyword.next_search_after = calculate_next_run(
            datetime.utcnow(), settings.keyword_search_cooldown_minutes
        )
        inserted += 1

    if inserted:
        db.commit()

    return inserted


def fill_daily_queue(db: Session) -> dict:
    """Ensure queue has enough jobs for the day respecting daily cap."""

    daily_cap = settings.keyword_daily_search_cap
    batch_size = settings.keyword_scheduler_batch_size

    pending_jobs = (
        db.query(KeywordSearchQueue)
        .filter(KeywordSearchQueue.status == "pending")
        .count()
    )

    remaining_capacity = max(daily_cap - pending_jobs, 0)
    if remaining_capacity <= 0:
        logger.info("Keyword queue already at daily capacity: %s", pending_jobs)
        return {"queued": 0, "pending_jobs": pending_jobs}

    limit = min(batch_size, remaining_capacity)
    candidates = load_eligible_keywords(db, limit=limit)
    queued = queue_keywords(db, candidates)

    logger.info("Queued %s keywords (pending=%s)", queued, pending_jobs + queued)

    return {
        "queued": queued,
        "pending_jobs": pending_jobs + queued,
        "requested": limit,
        "candidates": len(candidates),
    }


def mark_keyword_searched(db: Session, keyword: Keyword) -> None:
    """Update keyword scheduling metadata after search completes."""

    now = datetime.utcnow()
    keyword.last_searched = now
    keyword.next_search_after = calculate_next_run(
        now, settings.keyword_search_cooldown_minutes
    )
    keyword.search_count = (keyword.search_count or 0) + 1
    db.add(keyword)


def dequeue_jobs(db: Session, limit: int) -> List[KeywordSearchQueue]:
    """Fetch pending jobs ordered by priority and schedule."""

    jobs = (
        db.query(KeywordSearchQueue)
        .filter(
            KeywordSearchQueue.status == "pending",
            KeywordSearchQueue.scheduled_at <= datetime.utcnow(),
        )
        .order_by(KeywordSearchQueue.priority.desc(), KeywordSearchQueue.scheduled_at)
        .limit(limit)
        .with_for_update(skip_locked=True)
        .all()
    )

    for job in jobs:
        job.status = "running"
        job.last_attempt_at = datetime.utcnow()
        job.attempts = (job.attempts or 0) + 1
        db.add(job)

    if jobs:
        db.commit()

    return jobs


def complete_job(
    db: Session, job: KeywordSearchQueue, *, success: bool, error: Optional[str] = None
) -> None:
    """Finalize a job after execution."""

    now = datetime.utcnow()
    job.updated_at = now

    if success:
        job.status = "completed"
        job.error = None
    else:
        job.status = (
            "failed" if (job.attempts or 0) >= (job.max_attempts or 3) else "pending"
        )
        job.error = error
        if job.status == "pending":
            job.scheduled_at = calculate_next_run(
                now, settings.keyword_scheduler_retry_minutes
            )

    db.add(job)
    db.commit()


def reset_stale_jobs(db: Session, stale_minutes: int = 30) -> int:
    """Requeue jobs stuck in running state beyond stale threshold."""

    cutoff = datetime.utcnow() - timedelta(minutes=stale_minutes)
    stale_jobs = (
        db.query(KeywordSearchQueue)
        .filter(
            KeywordSearchQueue.status == "running",
            KeywordSearchQueue.last_attempt_at < cutoff,
        )
        .all()
    )

    for job in stale_jobs:
        job.status = "pending"
        job.scheduled_at = datetime.utcnow()
        db.add(job)

    if stale_jobs:
        db.commit()

    return len(stale_jobs)
