# Changelog

All notable changes to the European News Intelligence Hub (EUINT) project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-21

### Added
- Initial production release
- Full-stack AI-powered news aggregation platform
- Dual-layer sentiment analysis (VADER + Gemini)
- Semantic search with pgvector and sentence-transformers
- Multi-language support (9 languages)
- 11-service microservices architecture with Docker Compose
- Comprehensive monitoring stack (Prometheus, Grafana, AlertManager)
- Automated keyword management and approval system
- Pre-aggregation performance optimization (170x improvement)
- Background task processing with Celery
- Admin dashboard for source and keyword management
- API documentation via FastAPI /docs
- 84% test coverage with pytest
- Production deployment guides and scripts

### Architecture Patterns
- Dual-Layer AI Processing with Fallback
- Pre-Aggregation for Performance (sentiment trends)
- pgvector Semantic Search
- Pydantic Settings Management
- Microservices with Health Checks
- Async FastAPI with Middleware Stack
- Celery Background Tasks with Beat Scheduler
- Multi-Language Support

### Security
- SecurityHeadersMiddleware for HTTP headers
- Rate limiting (60 req/min default)
- CORS with environment-aware origins
- Admin authentication (basic auth)
- API key management via environment variables
- SQL injection prevention via SQLAlchemy ORM

### Performance
- Pre-aggregated sentiment trends (5ms vs 850ms)
- Batch embedding generation (3-5x faster)
- Redis caching for API responses
- Database connection pooling
- Async I/O operations

### Monitoring
- Prometheus metrics collection
- Grafana dashboards
- Custom exporters (postgres, redis, node)
- AlertManager for alerting
- Structured logging with log levels
- Health check endpoints for all services

## [Unreleased]

### Planned
- OAuth/JWT authentication
- API versioning
- Data retention policies
- Enhanced error recovery mechanisms
- Integration tests for Celery tasks
- CDN for frontend static assets
- Additional caching strategies
