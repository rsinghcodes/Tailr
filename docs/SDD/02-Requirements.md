# Requirements

**Project:** Tailr

**Document Version:** 1.0

**Status:** Draft

**Last Updated:** July 2026

---

# 1. Introduction

## 1.1 Purpose

This document defines the functional and non-functional requirements for **Tailr**, an Agentic Career Intelligence Platform.

It serves as the foundation for system architecture, implementation, testing, and future enhancements.

The purpose of this document is to clearly define what the system must do before describing how it will be implemented.

---

## 1.2 Scope

Tailr enables users to optimize resumes for specific job descriptions using AI while ensuring:

- factual correctness
- explainable modifications
- ATS optimization
- deterministic document generation
- reproducible workflows

The system accepts a master resume written in LaTeX and produces tailored resume variants without modifying the user's factual information.

---

# 2. Stakeholders

| Stakeholder | Responsibility              |
| ----------- | --------------------------- |
| Candidate   | Uses the platform           |
| Developer   | Builds and maintains Tailr  |
| AI Agent    | Performs reasoning tasks    |
| Validator   | Ensures factual correctness |
| Recruiter   | Consumes optimized resumes  |
| ATS         | Evaluates generated resumes |

---

# 3. User Personas

## Student

Needs

- internship applications
- graduate roles
- ATS optimization

Pain Points

- little experience
- repetitive tailoring

---

## Software Engineer

Needs

- tailored resumes
- multiple resume versions
- keyword optimization

Pain Points

- many applications
- manual rewriting

---

## AI Engineer

Needs

- emphasize GenAI experience
- optimize projects
- highlight research

Pain Points

- difficult to match AI-specific JDs

---

# 4. Functional Requirements

## FR-001 Resume Upload

Priority

Critical

Description

The system shall allow users to upload a master resume.

Supported formats

- LaTeX (.tex)

Future

- PDF
- DOCX

Acceptance Criteria

- upload succeeds
- parser validates structure

---

## FR-002 Resume Parsing

Priority

Critical

The parser shall convert LaTeX into a canonical structured model.

Output

```json
{
  "summary": "",
  "skills": [],
  "experience": [],
  "projects": []
}
```

Acceptance Criteria

- parser extracts all supported sections
- parser detects invalid templates
- parser produces deterministic output

---

## FR-003 Resume Validation

Priority

Critical

The system shall verify:

- dates
- companies
- project count
- skills
- formatting consistency

The validator shall reject invalid outputs.

---

## FR-004 Job Description Upload

Supported

- text
- PDF
- DOCX

Future

- LinkedIn URL
- company careers page

---

## FR-005 JD Analysis

The system shall identify

- title
- responsibilities
- required skills
- preferred skills
- soft skills
- ATS keywords

Output shall be structured JSON.

---

## FR-006 Knowledge Indexing

The system shall create searchable indexes for

- Resume
- Projects
- Experience
- Skills
- Job Descriptions
- Resume Versions
- Career Guides

---

## FR-007 Semantic Retrieval

The system shall retrieve only relevant information before invoking the LLM.

Retrieval sources

- Resume Knowledge Base
- Job Description Index
- Career Knowledge Base

---

## FR-008 Rewrite Planning

The planner shall generate an optimization plan before rewriting.

The plan shall specify

- sections to modify
- keywords to introduce
- bullet ordering
- suggested emphasis

---

## FR-009 Resume Rewriting

The rewrite agent shall

- improve wording
- reorder bullets
- improve readability
- increase keyword coverage

The rewrite agent shall not

- invent skills
- invent projects
- invent metrics
- invent employers
- invent dates

---

## FR-010 Validation

Every generated resume shall pass validation.

Validation includes

- schema validation
- factual validation
- hallucination detection
- formatting validation

---

## FR-011 ATS Analysis

The system shall generate

- ATS score
- keyword coverage
- missing skills
- readability score
- optimization recommendations

---

## FR-012 Resume Rendering

The renderer shall generate

- resume.tex
- PDF

Renderer output shall compile successfully.

---

## FR-013 Version Management

The system shall store

- original resume
- optimized versions
- ATS reports
- optimization plans
- diffs

---

## FR-014 Change Report

The system shall explain

- every modification
- reason
- affected section
- supporting JD requirement

---

## FR-015 User Review

Users shall review changes before export.

---

# 5. Non-Functional Requirements

## Performance

Resume parsing

< 1 second

Retrieval

< 500 ms

Optimization

< 15 seconds

Rendering

< 3 seconds

---

## Reliability

- deterministic parser
- retry failed agents
- recover from LLM failures

Target uptime

99%

---

## Scalability

Support

- multiple resumes
- multiple JDs
- version history

Future

multi-user deployment

---

## Maintainability

Each module shall have

- single responsibility
- unit tests
- API documentation

---

## Explainability

Every recommendation shall contain

- reason
- evidence
- confidence

---

## Security

The system shall

- protect uploaded resumes
- isolate prompts
- sanitize user input
- validate uploaded files

---

## Privacy

No resume data shall be shared with third-party services unless explicitly configured.

The system shall support fully local execution.

---

## Portability

Tailr shall run on

- Windows
- Linux
- macOS

using Docker.

---

# 6. Constraints

Technical

- Python backend
- FastAPI
- LlamaIndex
- Qdrant
- Ollama
- PostgreSQL

Project

- Open source
- Student friendly
- Minimal cloud cost

---

# 7. Assumptions

- User owns a master resume.
- Resume information is truthful.
- Job descriptions are well formatted.
- Users review generated resumes.

---

# 8. Out of Scope

The first release will not support

- automatic job applications
- recruiter messaging
- interview scheduling
- salary prediction
- resume fabrication

---

# 9. Acceptance Criteria

The MVP is complete when:

✓ Resume parser works

✓ Renderer reproduces original LaTeX

✓ Job description parser extracts structured data

✓ Resume optimization succeeds

✓ Validation prevents hallucinations

✓ PDF compiles successfully

✓ ATS report generated

✓ User can download optimized resume

---

# 10. Success Metrics

Engineering

- Parser accuracy > 99%

- Rendering success > 99%

- Retrieval precision > 90%

- Validation precision > 95%

- API latency < 2 seconds

---

User Experience

- Resume optimization < 30 seconds

- Manual editing reduced by 70%

- ATS score improvement

- High user satisfaction

---

# 11. Risks

| Risk           | Impact | Mitigation             |
| -------------- | ------ | ---------------------- |
| Hallucinations | High   | Validation Engine      |
| Invalid LaTeX  | High   | Deterministic Renderer |
| Poor Retrieval | Medium | Hybrid Search          |
| Model Drift    | Medium | Prompt Versioning      |
| Slow Responses | Medium | Caching                |

---

# 12. Future Requirements

The platform should eventually support

- Cover Letter Generation

- LinkedIn Optimization

- Portfolio Optimization

- GitHub Analysis

- Career Knowledge Graph

- Interview Preparation

- Resume Analytics

- Application Tracking

- Recruiter Feedback Learning

- Multi-language Resume Support

---

# 13. Requirement Traceability

| Requirement     | Component           |
| --------------- | ------------------- |
| Resume Upload   | Upload Service      |
| Resume Parsing  | Parser Engine       |
| Knowledge Index | LlamaIndex          |
| Retrieval       | Qdrant              |
| Planning        | Planner Agent       |
| Rewrite         | Rewrite Agent       |
| Validation      | Rule Engine         |
| ATS Analysis    | ATS Engine          |
| Rendering       | LaTeX Renderer      |
| PDF             | Compilation Service |

---

# 14. Exit Criteria

The Requirements phase is complete when

- all functional requirements are approved
- architecture can be derived without ambiguity
- implementation milestones are defined
- acceptance criteria are measurable
- stakeholders agree on project scope
