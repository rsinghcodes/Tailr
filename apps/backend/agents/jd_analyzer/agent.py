import json
import logging
import re
from agents.jd_analyzer.schemas import JDAnalysisOutput
from domain.shared.llm_provider import LLMProvider

logger = logging.getLogger(__name__)


class JDAnalyzerAgent:
    """Agent responsible for analyzing job descriptions and extracting structured requirements using AI reasoning."""

    def __init__(self, llm_provider: LLMProvider | None = None):
        self.llm_provider = llm_provider

    async def analyze(self, job_description_text: str) -> JDAnalysisOutput:
        if not job_description_text or not job_description_text.strip():
            return JDAnalysisOutput()

        if self.llm_provider and hasattr(self.llm_provider, "generate"):
            try:
                system_prompt = (
                    "You are an expert technical recruiter and Job Description Analyzer AI Agent. "
                    "Analyze the given Job Description and extract structured requirements as JSON with the following keys:\n"
                    "- required_skills: list of mandatory technical skills/tools\n"
                    "- preferred_skills: list of nice-to-have skills/tools\n"
                    "- seniority: seniority level (e.g. Junior, Mid, Senior, Lead, Staff)\n"
                    "- domain: primary engineering domain (e.g. Backend, Full Stack, AI Engineering, Cloud/DevOps)\n"
                    "- priority_keywords: top 5-10 core ATS keywords to optimize for\n"
                    "- responsibilities: list of core job responsibilities\n"
                    "Return ONLY valid JSON matching this schema."
                )

                res = await self.llm_provider.generate(
                    prompt=f"Job Description Text:\n{job_description_text}",
                    system_prompt=system_prompt,
                    response_model=JDAnalysisOutput,
                    model="qwen3:8b",
                )

                if isinstance(res, JDAnalysisOutput):
                    return res

                if isinstance(res, dict):
                    return JDAnalysisOutput.model_validate(res)

                if isinstance(res, str):
                    # Clean potential markdown formatting
                    cleaned = re.sub(r"```json\s*", "", res)
                    cleaned = re.sub(r"```\s*$", "", cleaned).strip()
                    parsed = json.loads(cleaned)
                    return JDAnalysisOutput.model_validate(parsed)
            except Exception as exc:
                logger.warning("LLM JD analysis failed, using fallback extraction: %s", str(exc))

        # Fallback heuristic extraction from text
        words = set(re.findall(r"\b[A-Za-z0-9+#.-]{2,}\b", job_description_text))
        tech_vocab = {
            "Python", "FastAPI", "Docker", "PostgreSQL", "Redis", "Qdrant", "Kubernetes",
            "React", "TypeScript", "Next.js", "LangGraph", "AWS", "CI/CD", "REST", "GraphQL",
            "SQL", "Git", "Linux", "PyTorch", "TensorFlow", "Microservices", "System Design"
        }
        found_skills = [s for s in tech_vocab if any(w.lower() == s.lower() for w in words)]
        
        return JDAnalysisOutput(
            required_skills=found_skills[:5] if found_skills else ["Python", "Software Engineering"],
            preferred_skills=found_skills[5:10] if len(found_skills) > 5 else ["Docker", "CI/CD"],
            seniority="Mid-Senior" if any(k in job_description_text.lower() for k in ["senior", "lead", "staff"]) else "Mid",
            domain="AI & Software Platform Engineering",
            priority_keywords=found_skills[:8] if found_skills else ["Software Engineering", "APIs"],
            responsibilities=["Design and maintain software systems.", "Collaborate with engineering teams."],
        )
