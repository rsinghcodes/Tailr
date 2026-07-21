# Parser Module — Production Implementation Prompt

## Objective

Implement the complete production-ready **Parser Module** for Tailr.

This module converts LaTeX resumes into the Canonical Resume Model using compiler-inspired techniques — without any LLM involvement.

The Parser Module is responsible for:

- file validation and security scanning,
- lexical analysis (tokenization),
- parsing into an Abstract Syntax Tree (AST),
- semantic analysis and entity extraction,
- technology normalization,
- entity resolution,
- Canonical Resume Model construction,
- source mapping for traceability,
- error recovery,
- template support,
- and deterministic, reproducible output.

The parser is **pure software** and must never call an LLM.

---

# Read First

Mandatory documents:

- AGENTS.md
- workflow.md
- architecture.md
- rules/architecture.md
- rules/python.md
- rules/security.md
- rules/testing.md
- ADR-0001 — Canonical Resume Model
- ADR-0002 — Clean Architecture
- 07-Parser-Architecture.md
- 05-Data-Models.md

If any implementation conflicts with these documents, follow the ADRs and architecture documents.

---

# Architecture Constraints

The parser is part of the **Infrastructure Layer** but produces domain entities.

### Allowed

- File I/O (reading uploaded files)
- Lexical analysis
- AST construction
- Semantic analysis
- Normalization
- Validation

### Forbidden

- LLM calls
- Database access
- HTTP requests
- Business logic beyond parsing
- Prompt generation
- Guardrail invocation (file-level security scanning is a parser responsibility; AI output guardrails are separate)

---

# Parser Pipeline

```text
resume.tex
     │
     ▼
File Validation & Security Scan
     │
     ▼
Lexer (Tokenization)
     │
     ▼
Parser (AST Construction)
     │
     ▼
Semantic Analyzer
     │
     ▼
Intermediate Representation
     │
     ▼
Canonical Resume Model
     │
     ▼
Knowledge Builder (downstream)
```

---

# Stage 1 — File Validation & Security Scan

### Responsibilities

- verify file extension (.tex)
- verify UTF-8 encoding
- enforce maximum file size (configurable)
- validate MIME type using file signature inspection
- detect unsupported LaTeX packages
- check for required template markers
- detect malformed LaTeX
- detect suspicious LaTeX commands
- reject shell-escape directives (`\write18`, `\input`, `\include`, `\openout`, `\catcode`)
- normalize line endings
- sanitize file metadata

### Output

```text
ValidatedSourceFile
```

### Failure Modes

- `InvalidFileTypeError`
- `InvalidEncodingError`
- `FileTooLargeError`
- `UnsupportedTemplateError`
- `UnsafeLaTeXCommandError`
- `CorruptedSourceError`

---

# Stage 2 — Lexical Analysis (Lexer)

Convert raw LaTeX source into tokens.

### Token Types

```text
SECTION, SUBSECTION, COMMAND, TEXT, ARGUMENT,
ENVIRONMENT, COMMENT, NEWLINE, BRACE_OPEN,
BRACE_CLOSE, BRACKET_OPEN, BRACKET_CLOSE, EOF
```

### Each Token Contains

- value
- token_type
- line
- column
- source_file

### Requirements

- preserve source locations for every token
- ignore comments
- handle nested braces
- handle LaTeX environments
- preserve macro boundaries

---

# Stage 3 — Parsing (AST Construction)

Convert tokens into an Abstract Syntax Tree.

### AST Node Types

```text
ResumeNode
├── SectionNode
│   ├── ExperienceNode
│   ├── ProjectNode
│   ├── SkillNode
│   ├── EducationNode
│   └── AchievementNode
├── BulletNode
├── TextNode
└── CommandNode
```

### Each Node Stores

- type
- content
- children
- source location (line, column)
- template metadata

### Requirements

- validate document structure
- detect missing required sections
- detect duplicate sections
- detect empty sections
- attempt error recovery for non-critical failures

---

# Stage 4 — Semantic Analysis

Convert AST nodes into domain entities.

### Responsibilities

- normalize dates (various formats → ISO)
- normalize technology names (canonical dictionary)
- detect and merge duplicate entities
- validate required fields per entity type
- build cross-entity relationships
- resolve aliases
- infer section semantics from template macros
- attach validation metadata

---

# Stage 5 — Intermediate Representation

Before building the canonical model, produce a template-independent IR.

```text
AST → IR → Canonical Resume Model
```

The IR removes template-specific details so that different templates (Jake's, ModernCV, Tailr Default) all map to the same canonical structure.

---

# Stage 6 — Canonical Resume Model Construction

Produce the final `Resume` entity as defined in the domain layer.

### Output

```python
Resume(
    summary=ResumeSummary(),
    experience=list[Experience],
    projects=list[Project],
    skills=list[SkillCategory],
    education=list[Education],
    certifications=list[Certification],
    achievements=list[Achievement],
    metadata=ResumeMetadata(),
)
```

---

# Technology Normalization

Maintain a versioned canonical dictionary.

### Examples

```text
NodeJS → Node.js
JS → JavaScript
TS → TypeScript
Postgres → PostgreSQL
ReactJS → React
K8s → Kubernetes
```

The dictionary must be:

- versioned
- extensible
- configurable
- loaded at startup

---

# Source Mapping

Every parsed entity must keep a reference to its origin.

### Source Map Entry

```python
SourceLocation(
    file: str,
    start_line: int,
    end_line: int,
    start_column: int,
    end_column: int,
)
```

### Benefits

- explainability
- precise error reporting
- visual diff generation
- traceable AI modifications
- auditability

---

# Template Support

### Version 1

- Tailr Default Template
- Jake's Resume Template
- ModernCV (subset)

### Future

- AwesomeCV
- AltaCV
- Custom templates

Each template defines its own parsing rules and macro mappings via a `TemplateAdapter` interface.

---

# Error Recovery

The parser must attempt recovery rather than terminating on first error.

### Recovery Strategy

- unknown command → warning, continue
- missing bullet → validation warning, continue
- unclosed environment → auto-recovery attempt, continue
- critical structural failure → stop, report

Only critical failures stop parsing.

---

# Parser Outputs

The parser produces:

1. Canonical Resume Model
2. Abstract Syntax Tree
3. Intermediate Representation
4. Validation Report (warnings and errors)
5. Source Map
6. Parsing Metrics (duration, token count, node count)
7. Security Scan Report
8. Normalization Report (aliases resolved)

---

# Performance Targets

- Parsing time: **< 500 ms**
- Memory: **< 50 MB**
- Deterministic: **100%**
- Network requests: **0**
- Thread-safe: **Yes**

---

# Required File Structure

```text
parsers/
├── __init__.py
├── pipeline.py
├── lexer/
│   ├── __init__.py
│   ├── tokenizer.py
│   └── tokens.py
├── parser/
│   ├── __init__.py
│   ├── ast_parser.py
│   └── ast_nodes.py
├── semantic/
│   ├── __init__.py
│   ├── analyzer.py
│   ├── ir.py
│   └── builder.py
├── normalization/
│   ├── __init__.py
│   ├── technology.py
│   ├── dates.py
│   └── dictionary.py
├── templates/
│   ├── __init__.py
│   ├── base.py
│   ├── jakes.py
│   ├── moderncv.py
│   └── tailr_default.py
├── security/
│   ├── __init__.py
│   ├── file_validator.py
│   └── latex_scanner.py
├── source_map/
│   ├── __init__.py
│   └── mapper.py
├── models/
│   ├── __init__.py
│   ├── tokens.py
│   ├── ast.py
│   ├── ir.py
│   └── reports.py
└── exceptions.py
```

---

# Testing Requirements

Generate tests for:

- lexer (tokenization of various LaTeX constructs),
- parser (AST construction for valid and malformed input),
- semantic analyzer (entity extraction, date normalization),
- technology normalization (alias resolution, deduplication),
- template adapters (Jake's, ModernCV, Tailr Default),
- source mapping (line/column accuracy),
- error recovery (graceful degradation),
- golden tests (resume.tex → expected canonical JSON),
- regression tests (behavior stability),
- fuzz tests (random malformed LaTeX),
- security tests (oversized files, invalid encodings, shell-escape, path traversal),
- and performance tests (< 500 ms target).

Use: pytest, parameterized tests, golden test fixtures.

Target coverage: **95%+** for parser modules.

---

# Quality Requirements

Generated code must:

- pass Ruff,
- pass MyPy (strict),
- use full type hints,
- include docstrings,
- contain no LLM calls,
- be deterministic,
- be thread-safe,
- avoid global mutable state,
- and be production deployable.

---

# Output Requirements

Return:

1. complete source files,
2. test files,
3. golden test fixtures (sample .tex → expected JSON),
4. normalization dictionary,
5. template adapter documentation,
6. parser pipeline explanation,
7. error recovery strategy explanation,
8. security scanning explanation,
9. performance benchmarks,
10. and any trade-offs made.

Do not return partial implementations, placeholders, or pseudocode.

---

# Final Instruction

Generate a **complete production-ready Parser Module** that provides:

- compiler-inspired LaTeX parsing,
- deterministic canonical model construction,
- multi-template support,
- technology normalization,
- source mapping,
- error recovery,
- security scanning,
- and comprehensive testing

for the Tailr platform.
