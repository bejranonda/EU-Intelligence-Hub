# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-01-19

### Added
- **Major Workspace Organization**: Reorganized 57 scattered markdown files into logical `docs/` directory structure
- **Comprehensive Research Materials**: Added extensive UX/UI design research for 2025
- **Multi-language Support Documentation**: Complete documentation for EN, TH, DE, and DA languages
- **Product Strategy Research**: Comprehensive product strategy research reports
- **Validation Reports**: Detailed test validation and quality control documentation
- **Navigation READMEs**: Added README.md files in all documentation directories

### Fixed
- **TypeScript Compilation Errors**: Resolved all remaining TypeScript compilation errors in frontend and workflow files
- **GitHub Workflow Bug**: Fixed auto-pr workflow issue with undefined pull_request context
- **Type Definitions**: Updated with comprehensive change notes

### Changed
- **Project Structure**: Moved from flat structure to organized hierarchy with specialized directories
- **Documentation Layout**: Reorganized research into Archive, Roadmap, and UX/UI categories
- **File Organization**: Grouped technical documentation by purpose (audit, analysis, fixes, reports, etc.)

### Improved
- **Developer Experience**: Significantly improved navigation and file discoverability
- **Documentation Quality**: Enhanced documentation consistency and completeness
- **Project Maintainability**: Better organized structure for ongoing development
- **Code Quality**: All TypeScript compilation issues resolved

## [1.0.0] - 2025-01-15

### Added
- **Initial Release**: Complete European News Intelligence Hub platform
- **Backend API**: FastAPI-based REST API with 30+ endpoints
- **Frontend Interface**: React TypeScript application with modern UI
- **Database Integration**: PostgreSQL with pgvector for semantic search
- **AI Services**: Google Gemini integration for sentiment analysis
- **Multi-language Support**: Support for 9 languages (EN, TH, DE, FR, ES, IT, PL, SV, NL)
- **Sentiment Analysis**: Dual-layer analysis (VADER + Gemini)
- **Semantic Search**: 384-dimensional vector embeddings
- **Mind Maps**: Interactive relationship visualization
- **Automated Collection**: Hourly Celery tasks for news scraping
- **Admin Interface**: Complete admin panel for source and keyword management
- **Docker Orchestration**: 11 services in production-ready setup
- **Monitoring**: Prometheus + Grafana integration
- **SSL Support**: Let's Encrypt automation
- **Comprehensive Testing**: 49 tests with >80% coverage

### Features
- **Real-time News Aggregation**: From 12 European news sources
- **Sentiment Trends**: Daily precomputed sentiment analysis
- **Keyword Management**: AI-powered keyword suggestions and translations
- **Document Upload**: PDF processing and analysis
- **Search Functionality**: Full-text and semantic search capabilities
- **Visualization**: Interactive timelines and mind maps
- **Multi-language Interface**: Complete i18n support
- **Admin Dashboard**: Source management and approval workflows

---

## Version Classification

- **Major (X.0.0)**: Breaking changes, major feature additions
- **Minor (x.Y.0)**: New features, non-breaking additions
- **Patch (x.y.Z)**: Bug fixes, documentation improvements, optimizations

## Project Statistics

- **Codebase**: ~9,800 lines of code
- **Languages**: Python (5,100 lines), TypeScript (1,800 lines)
- **API Endpoints**: 30+ across 8 routers
- **Database Tables**: 12 with pgvector support
- **Test Coverage**: 49 tests, >80% coverage
- **Docker Services**: 11 in production setup
- **Documentation**: 40+ markdown files

## Support

For issues, questions, or contributions:
- 📖 Documentation: [README.md](README.md)
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions
- 📧 Contact: Project maintainers