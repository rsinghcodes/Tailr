import logging
import re
from typing import Optional
from domain.shared.llm_provider import LLMProvider
from prompts.registry import PromptRegistry
from domain.job_description.models import JobDescription, JobRequirements

logger = logging.getLogger(__name__)


def _heuristic_extract(jd: JobDescription) -> JobRequirements:
    """Fallback heuristic extraction when LLM is unavailable."""
    text = jd.description or ""
    words = set(re.findall(r"\b[A-Za-z0-9+#.-]{2,}\b", text))

    tech_vocab = {
        "Python", "FastAPI", "Docker", "PostgreSQL", "Redis", "Qdrant", "Kubernetes",
        "React", "TypeScript", "Next.js", "LangGraph", "AWS", "CI/CD", "REST", "GraphQL",
        "SQL", "Git", "Linux", "PyTorch", "TensorFlow", "Microservices", "System Design",
        "Java", "Go", "Rust", "C++", "Node.js", "Express", "MongoDB", "Elasticsearch",
        "Kafka", "RabbitMQ", "Terraform", "Ansible", "Jenkins", "GitHub Actions",
        "DynamoDB", "Cassandra", "Spark", "Airflow", "dbt", "Snowflake",
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "LLM",
        "RAG", "Vector Database", "Embedding", "Fine-tuning", "Agentic",
        "Scrum", "Agile", "JIRA", "Confluence",
    }
    found = [s for s in tech_vocab if any(w.lower() == s.lower() for w in words)]

    lower_text = text.lower()
    seniority = "Mid"
    if any(k in lower_text for k in ["staff", "principal", "distinguished"]):
        seniority = "Staff"
    elif any(k in lower_text for k in ["senior", "sr.", "lead"]):
        seniority = "Senior"
    elif any(k in lower_text for k in ["junior", "jr.", "entry", "intern"]):
        seniority = "Junior"

    return JobRequirements(
        required_skills=found[:8] if found else ["Python", "Software Engineering"],
        preferred_skills=found[8:15] if len(found) > 8 else [],
        keywords=found[:10] if found else ["Software Engineering", "APIs"],
        experience_level=seniority,
    )


class JobDescriptionAnalyzer:
    """Application service to analyze job description texts and extract structured requirements."""

    def __init__(self, llm_provider: LLMProvider, prompt_registry: PromptRegistry):
        self.llm_provider = llm_provider
        self.prompt_registry = prompt_registry

    async def analyze(
        self,
        jd: JobDescription,
        model: Optional[str] = None,
        temperature: float = 0.0,
    ) -> JobRequirements:
        try:
            system_prompt = self.prompt_registry.get_prompt("jd_analyzer", "system", "v1")
            user_template = self.prompt_registry.get_prompt("jd_analyzer", "user", "v1")

            user_prompt = user_template.format(
                title=jd.title,
                company=jd.company or "Unknown Company",
                description=jd.description
            )

            requirements: JobRequirements = await self.llm_provider.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                schema=JobRequirements,
                temperature=temperature,
                model=model
            )
            return requirements
        except Exception as exc:
            logger.warning("LLM JD analysis failed, using heuristic fallback: %s", str(exc))
            return _heuristic_extract(jd)
