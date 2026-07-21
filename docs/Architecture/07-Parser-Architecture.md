# Parser Architecture

**Project:** Tailr
**Version:** 1.0

---

# 1. Purpose

The Parser is responsible for converting a user’s LaTeX resume into a structured, validated, and canonical representation used throughout Tailr.

Unlike traditional resume parsers that rely on OCR, regex, or LLMs, Tailr treats the resume as source code and parses it using compiler-inspired techniques.

The parser is deterministic, reproducible, and independent of any Large Language Model.

---

# 2. Design Goals

The parser must:

- Produce deterministic output
- Preserve every factual detail
- Detect malformed templates
- Support validation
- Build a canonical resume model
- Generate semantic entities for RAG
- Be independent from AI agents
- Support source-level traceability
- Support secure file processing

The parser never performs rewriting or optimization.

---

# 3. Why Not Use an LLM?

Using an LLM for parsing introduces several risks:

- Hallucinated fields
- Inconsistent JSON
- Missing sections
- Non-deterministic behavior
- Higher latency
- Increased cost

The parser should be pure software.

LLMs are reserved for reasoning, not extraction.

---

# 4. Parser Pipeline

```text
                resume.tex
                     │
                     ▼
            File Validation & Guardrails
                     │
                     ▼
                  Lexer
                     │
                     ▼
                  Tokens
                     │
                     ▼
                  Parser
                     │
                     ▼
            Abstract Syntax Tree
                     │
                     ▼
           Semantic Analyzer
                     │
                     ▼
        Canonical Resume Model
                     │
                     ▼
          Knowledge Builder
```

---

# 5. Stage 1 — File Validation & Guardrails

Responsibilities

- Verify extension (.tex)
- Verify UTF-8 encoding
- Detect unsupported packages
- Check required template markers
- Detect malformed LaTeX
- Enforce maximum file size
- Validate MIME type
- Detect suspicious LaTeX commands
- Reject embedded shell-escape directives
- Normalize line endings
- Sanitize file metadata

Outputs

```text
Validated Source File
```

Failures

- Missing file
- Invalid encoding
- Unsupported template
- Corrupted source
- File too large
- Suspicious LaTeX command
- Unsafe compilation directive

This stage acts as the first security boundary before any parsing occurs.

---

# 6. Stage 2 — Lexical Analysis

The lexer converts raw LaTeX into tokens.

Example

Input

```latex
\section{Experience}

\resumeItem{Built scalable REST APIs}
```

Output

```text
SECTION
TEXT
COMMAND
ARGUMENT
```

Responsibilities

- Tokenization
- Ignore comments
- Ignore whitespace
- Preserve source locations
- Preserve macro boundaries
- Preserve environment boundaries

---

# 7. Token Types

Examples

```text
SECTION
SUBSECTION
COMMAND
TEXT
ARGUMENT
ENVIRONMENT
COMMENT
NEWLINE
EOF
```

Each token contains

```text
value
line
column
type
source_file
```

---

# 8. Stage 3 — Parsing

The parser converts tokens into an Abstract Syntax Tree (AST).

Example

```text
Resume
├── Summary
├── Experience
│   ├── Company
│   ├── Role
│   └── Bullet
├── Projects
├── Skills
└── Education
```

The parser validates document structure and attempts error recovery where possible.

---

# 9. AST Design

The AST preserves hierarchy.

```text
ResumeNode
SectionNode
ExperienceNode
ProjectNode
SkillNode
EducationNode
BulletNode
TextNode
CommandNode
```

Each node stores:

- type
- content
- children
- source location
- template metadata

---

# 10. Stage 4 — Semantic Analysis

The semantic analyzer converts AST nodes into domain entities.

Example

```text
ExperienceNode
↓
Experience
```

Responsibilities

- Normalize dates
- Normalize technologies
- Detect duplicates
- Validate required fields
- Build relationships
- Resolve aliases
- Infer section semantics
- Attach validation metadata

---

# 11. Canonical Resume Model

Output

```python
Resume(
    summary=Summary(),
    experience=list[Experience],
    projects=list[Project],
    skills=list[SkillCategory],
    education=list[Education],
    certifications=list[Certification],
    achievements=list[Achievement],
    metadata=ResumeMetadata(),
)
```

This model becomes the system’s single source of truth.

---

# 12. Validation Rules

The parser validates:

## Structure

- Required sections
- Section order
- Duplicate sections
- Empty sections

---

## Experience

- Company exists
- Role exists
- Valid dates
- At least one bullet
- Date ranges do not overlap unexpectedly

---

## Projects

- Title exists
- Technologies exist
- At least one description bullet

---

## Skills

- Categories valid
- Duplicate skills removed
- Skills normalized to canonical names

---

## Education

- Institution exists
- Degree exists
- Graduation year valid

---

# 13. Error Recovery

Rather than terminating immediately, the parser attempts recovery.

Example

```text
Unknown Command
↓
Warning
↓
Continue
```

Example

```text
Missing Bullet
↓
Validation Warning
↓
Continue
```

Example

```text
Unclosed Environment
↓
Attempt Auto-Recovery
↓
Continue Parsing
```

Only critical structural failures stop parsing.

---

# 14. Template Support

Version 1 supports

- Tailr Default Template
- Jake’s Resume Template
- ModernCV (subset)

Future support

- AwesomeCV
- AltaCV
- Custom templates

Each template defines its own parsing rules and macro mappings.

---

# 15. Intermediate Representation (IR)

Before building the canonical model, the parser creates an Intermediate Representation.

```text
AST
↓
IR
↓
Canonical Model
```

The IR removes template-specific details.

Example

```text
resumeSubheading
↓
ExperienceEntry
```

Different templates map to the same IR.

---

# 16. Technology Normalization

Technologies are normalized using a canonical dictionary.

Example

```text
NodeJS
↓
Node.js
```

```text
JS
↓
JavaScript
```

```text
TS
↓
TypeScript
```

The normalization dictionary is versioned and extensible.

This improves retrieval quality and ATS scoring.

---

# 17. Entity Resolution

Equivalent entities are merged.

Example

```text
ReactJS
↓
React
```

```text
Postgres
↓
PostgreSQL
```

The parser maintains canonical names and alias mappings.

---

# 18. Source Mapping

Every parsed entity keeps a reference to its origin.

Example

```text
Experience
↓
resume.tex
↓
Line 53
```

Benefits

- Explainability
- Precise error reporting
- Safe rendering
- Visual diff generation
- Traceable AI modifications
- Auditability

---

# 19. Knowledge Generation

The parser does not generate embeddings directly.

Instead it emits semantic entities.

```text
Experience
↓
Knowledge Builder
↓
Chunk
↓
Embedding
↓
Qdrant
```

This keeps parsing independent of indexing and vector infrastructure.

---

# 20. Parser Outputs

The parser produces:

- Canonical Resume Model
- Abstract Syntax Tree
- Intermediate Representation
- Validation Report
- Source Map
- Parsing Metrics
- Security Scan Report
- Normalization Report

---

# 21. Performance Targets

Target parsing time

**< 500 ms**

Memory

**< 50 MB**

Deterministic

**100%**

Network requests

**0**

Thread-safe

**Yes**

---

# 22. Testing Strategy

## Unit Tests

- Lexer
- Parser
- Semantic Analyzer
- Technology Normalizer
- Entity Resolver

---

## Golden Tests

```text
resume.tex
↓
Canonical Model
↓
Expected JSON
```

---

## Regression Tests

Ensure parser behavior never changes unexpectedly.

---

## Fuzz Tests

Random malformed LaTeX inputs.

---

## Security Tests

- Oversized files
- Invalid encodings
- Suspicious LaTeX commands
- Shell-escape directives
- Path traversal attempts

---

# 23. Extensibility

Future capabilities

- PDF parser
- DOCX parser
- Markdown parser
- LinkedIn parser
- GitHub parser
- JSON resume parser

Each parser produces the same canonical model and validation report.

---

# 24. Architecture Decisions

| Decision                             | Rationale                            |
| ------------------------------------ | ------------------------------------ |
| Compiler-inspired design             | Deterministic and testable           |
| AST                                  | Preserve document structure          |
| Intermediate Representation          | Decouple templates from domain model |
| Canonical Resume Model               | Single source of truth               |
| Software-only parser                 | Avoid hallucinations                 |
| Source Mapping                       | Explainability and debugging         |
| Validation & Guardrails stage        | Secure and validate untrusted input  |
| Versioned normalization dictionaries | Consistent entity resolution         |

---

# 25. Summary

The Tailr Parser is a deterministic, compiler-inspired subsystem that transforms LaTeX resumes into structured knowledge.

By separating file validation, lexical analysis, parsing, semantic analysis, normalization, and canonical model generation, the parser becomes reliable, secure, testable, and extensible.

Instead of treating resumes as text, Tailr treats them as structured programs that can be validated, transformed, audited, and reasoned about safely.

The addition of file-level guardrails and source mapping ensures that the parser can serve as a trustworthy foundation for downstream retrieval, validation, rendering, and AI-assisted optimization workflows.
