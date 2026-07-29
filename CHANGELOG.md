# Changelog

## [Unreleased]

### Added
- JWT authentication with bcrypt password hashing
- User registration and login endpoints
- AuthGuard component for protected frontend routes
- DataManager modal for inline preview and reuse of extracted data
- DetailViews shared components (ParsedResumeView, JdDetailView)
- Section-by-section vector indexing for resumes and job descriptions
- Expanded extraction schema with proper nested Pydantic models (ExtractedExperience, ExtractedEducation, ExtractedProject, ExtractedCertification, ExtractedAchievement)

### Changed
- Switched from LlamaParse to LlamaExtract for direct byte-based document parsing
- Removed raw_text storage from resume_versions table and all related code
- Cleaned workflow state: removed raw_resume_text and job_description_text fields
- Frontend streaming now accumulates state from SSE events instead of double-executing the workflow
- Qdrant Cloud with Gemini embeddings (3072d) replaces LlamaCloud
- Embedding model: models/gemini-embedding-001
- Replaced hardcoded mock data with real service calls

### Removed
- LlamaDocParser and all LlamaParse dependencies
- raw_text column from resume_versions (with migration)
- Dead code: agents, parsers, qdrant, ollama, latex, rag, storage modules
- docs/ directory and associated documentation
- HeroStats, AuditLogTable, ResultsView, WorkflowWizard, ResumeManager, JobDescriptionManager components

## [2026-07-29] — 9801f41
- Remove LlamaParse and raw_text; expand extraction schema; fix streaming UI; add DataManager modal
