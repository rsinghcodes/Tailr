import time
from typing import Any
from guardrails.base import (
    BaseValidator,
    GuardrailContext,
    GuardrailResult,
    GuardrailResultStatus,
    GuardrailViolation,
    ViolationSeverity,
)


class HallucinationValidator(BaseValidator):
    name: str = "hallucination_validator"

    async def validate(self, content: Any, context: GuardrailContext) -> GuardrailResult:
        start_time = time.perf_counter()

        canonical_resume = context.canonical_resume
        if not canonical_resume:
            return GuardrailResult(
                status=GuardrailResultStatus.APPROVED,
                repaired_content=content,
                warnings=["Canonical resume not provided for hallucination validation"],
                execution_time_ms=(time.perf_counter() - start_time) * 1000,
            )

        # Extract known entities whether canonical_resume is dict or Pydantic model
        known_companies: set[str] = set()
        known_projects: set[str] = set()

        if isinstance(canonical_resume, dict):
            exps = canonical_resume.get("experience", [])
            for e in exps:
                c = e.get("company") if isinstance(e, dict) else getattr(e, "company", None)
                if c:
                    known_companies.add(c.lower())

            projs = canonical_resume.get("projects", [])
            for p in projs:
                t = p.get("title") if isinstance(p, dict) else getattr(p, "title", None)
                if t:
                    known_projects.add(t.lower())
        else:
            if hasattr(canonical_resume, "experience"):
                for e in canonical_resume.experience:
                    if getattr(e, "company", None):
                        known_companies.add(e.company.lower())
            if hasattr(canonical_resume, "projects"):
                for p in canonical_resume.projects:
                    if getattr(p, "title", None):
                        known_projects.add(p.title.lower())

        violations = []
        content_dict = content if isinstance(content, dict) else {}

        # Check experiences
        if "experience" in content_dict and isinstance(content_dict["experience"], list):
            for exp in content_dict["experience"]:
                company = exp.get("company", "").lower() if isinstance(exp, dict) else getattr(exp, "company", "").lower()
                if company and not any(known in company or company in known for known in known_companies):
                    violations.append(
                        GuardrailViolation(
                            code="HALLUCINATED_EMPLOYER",
                            message=f"Employer '{exp.get('company')}' was not present in the Canonical Resume Model",
                            severity=ViolationSeverity.CRITICAL,
                            field="experience.company",
                        )
                    )

        # Check projects
        if "projects" in content_dict and isinstance(content_dict["projects"], list):
            for proj in content_dict["projects"]:
                title = proj.get("title", "").lower() if isinstance(proj, dict) else getattr(proj, "title", "").lower()
                if title and not any(known in title or title in known for known in known_projects):
                    violations.append(
                        GuardrailViolation(
                            code="HALLUCINATED_PROJECT",
                            message=f"Project '{proj.get('title')}' was not present in the Canonical Resume Model",
                            severity=ViolationSeverity.CRITICAL,
                            field="projects.title",
                        )
                    )

        if violations:
            return GuardrailResult(
                status=GuardrailResultStatus.REJECTED,
                violations=violations,
                execution_time_ms=(time.perf_counter() - start_time) * 1000,
            )

        return GuardrailResult(
            status=GuardrailResultStatus.APPROVED,
            repaired_content=content,
            execution_time_ms=(time.perf_counter() - start_time) * 1000,
        )
