import datetime as dt

import pytest
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.models import Keyword, KeywordSearchQueue
from app.services import keyword_scheduler as scheduler


@pytest.fixture(autouse=True)
def override_settings(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "keyword_search_cooldown_minutes", 60)
    monkeypatch.setattr(settings, "keyword_daily_search_cap", 10)
    monkeypatch.setattr(settings, "keyword_scheduler_batch_size", 5)
    monkeypatch.setattr(settings, "keyword_scheduler_min_priority", 0)
    monkeypatch.setattr(settings, "keyword_scheduler_retry_minutes", 30)
    monkeypatch.setattr(settings, "keyword_scheduler_enabled", True)
    yield


def _create_keyword(session: Session, **kwargs) -> Keyword:
    keyword = Keyword(
        keyword_en=kwargs.get("keyword_en", "energy policy"),
        category=kwargs.get("category", "energy"),
        search_priority=kwargs.get("search_priority", 5),
        last_searched=kwargs.get("last_searched"),
        next_search_after=kwargs.get("next_search_after"),
    )
    session.add(keyword)
    session.commit()
    session.refresh(keyword)
    return keyword


def test_load_eligible_keywords_respects_cooldown(db_session: Session):
    now = dt.datetime.utcnow()
    _create_keyword(db_session, last_searched=now - dt.timedelta(minutes=30))
    eligible = scheduler.load_eligible_keywords(db_session)
    assert eligible == []


def test_load_eligible_keywords_returns_ready(db_session: Session):
    now = dt.datetime.utcnow()
    kw = _create_keyword(db_session, last_searched=now - dt.timedelta(hours=3))
    eligible = scheduler.load_eligible_keywords(db_session)
    assert len(eligible) == 1
    assert eligible[0].keyword.id == kw.id


def test_queue_keywords_skips_duplicates(db_session: Session):
    now = dt.datetime.utcnow()
    kw = _create_keyword(db_session, last_searched=now - dt.timedelta(hours=3))
    candidates = scheduler.load_eligible_keywords(db_session)
    first = scheduler.queue_keywords(db_session, candidates)
    second = scheduler.queue_keywords(db_session, candidates)
    assert first == 1
    assert second == 0
    queued = db_session.query(KeywordSearchQueue).filter_by(keyword_id=kw.id).all()
    assert len(queued) == 1


def test_fill_daily_queue_respects_cap(db_session: Session):
    now = dt.datetime.utcnow()
    for index in range(12):
        _create_keyword(
            db_session,
            keyword_en=f"keyword-{index}",
            last_searched=now - dt.timedelta(hours=4),
            search_priority=index,
        )

    result = scheduler.fill_daily_queue(db_session)
    assert result["queued"] == 5  # limited by batch size


def test_dequeue_and_complete_job_flow(db_session: Session):
    now = dt.datetime.utcnow()
    keyword = _create_keyword(db_session, last_searched=now - dt.timedelta(hours=4))
    candidate = scheduler.SchedulingCandidate(keyword=keyword, next_scheduled_at=now, priority=10)
    scheduler.queue_keywords(db_session, [candidate])

    jobs = scheduler.dequeue_jobs(db_session, limit=1)
    assert len(jobs) == 1
    job = jobs[0]
    assert job.status == "running"

    scheduler.complete_job(db_session, job, success=True)
    refreshed = db_session.query(KeywordSearchQueue).filter_by(id=job.id).first()
    assert refreshed.status == "completed"


def test_mark_keyword_searched_updates_fields(db_session: Session):
    keyword = _create_keyword(db_session, last_searched=None)
    scheduler.mark_keyword_searched(db_session, keyword)
    db_session.commit()
    db_session.refresh(keyword)
    assert keyword.last_searched is not None
    assert keyword.next_search_after > keyword.last_searched
