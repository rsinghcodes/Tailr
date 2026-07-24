import logging
from typing import Any
from workflows.state import WorkflowState, WorkflowStatus
from guardrails.pipeline import GuardrailsEngine
from guardrails.base import GuardrailContext, GuardrailResultStatus
from guardrails.exceptions import GuardrailRejectionError
from validators.engine import ValidationEngine

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """LangGraph-aligned event-driven workflow engine orchestrating AI agents, guardrails, and validation."""

    def __init__(self, guardrails_engine: GuardrailsEngine | None = None, validation_engine: ValidationEngine | None = None):
        self.guardrails = guardrails_engine or GuardrailsEngine()
        self.validation_engine = validation_engine or ValidationEngine()

    async def run_step_parse_resume(self, state: WorkflowState) -> WorkflowState:
        state.status = WorkflowStatus.PARSING
        state.telemetry.step_history.append("PARSING")
        logger.info("Executing parse_resume workflow step", extra={"workflow_id": state.workflow_id})
        if state.raw_resume_text:
            state.canonical_resume = {
                "summary": "Software Engineer experienced in Python, FastAPI, and Cloud systems.",
                "skills": [{"name": "Python"}, {"name": "FastAPI"}, {"name": "Docker"}],
                "experience": [
                    {
                        "company": "TechCorp",
                        "role": "Software Engineer",
                        "start_date": "2021-01",
                        "end_date": "2023-12",
                        "bullets": ["Developed microservices in Python and FastAPI."],
                    }
                ],
                "projects": [],
                "education": [],
            }
        return state

    async def run_step_jd_analysis(self, state: WorkflowState) -> WorkflowState:
        state.status = WorkflowStatus.JD_ANALYSIS
        state.telemetry.step_history.append("JD_ANALYSIS")
        logger.info("Executing analyze_jd workflow step", extra={"workflow_id": state.workflow_id})
        if state.job_description_text:
            state.job_requirements = {
                "required_skills": ["Python", "FastAPI", "Docker", "LangGraph"],
                "seniority": "Mid-Senior",
                "domain": "AI Platform Engineering",
            }
        return state

    async def run_step_retrieval(self, state: WorkflowState) -> WorkflowState:
        state.status = WorkflowStatus.RETRIEVAL
        state.telemetry.step_history.append("RETRIEVAL")
        logger.info("Executing retrieve_context workflow step", extra={"workflow_id": state.workflow_id})
        state.retrieved_context = (
            "Candidate built microservices using Python and FastAPI at TechCorp. Experience with Docker containers."
        )
        return state

    async def run_step_planning(self, state: WorkflowState) -> WorkflowState:
        state.status = WorkflowStatus.PLANNING
        state.telemetry.step_history.append("PLANNING")
        logger.info("Executing planning workflow step", extra={"workflow_id": state.workflow_id})
        state.rewrite_plan = {
            "target_sections": ["summary", "experience"],
            "strategy": "Highlight FastAPI, microservices, and Docker expertise for AI Platform role.",
        }
        return state

    async def run_step_rewrite(self, state: WorkflowState) -> WorkflowState:
        state.status = WorkflowStatus.REWRITING
        state.telemetry.step_history.append("REWRITING")
        logger.info("Executing rewrite workflow step", extra={"workflow_id": state.workflow_id})
        state.rewritten_resume = {
            "summary": "Senior Software Engineer specializing in Python, FastAPI, Docker, and AI workflow orchestration.",
            "experience": [
                {
                    "company": "TechCorp",
                    "role": "Software Engineer",
                    "start_date": "2021-01",
                    "end_date": "2023-12",
                    "bullets": [
                        "Architected scalable microservices using Python, FastAPI, and Docker.",
                        "Optimized retrieval pipelines and agentic workflows.",
                    ],
                }
            ],
        }
        return state

    async def run_step_guardrails(self, state: WorkflowState) -> WorkflowState:
        state.status = WorkflowStatus.GUARDRAILS
        state.telemetry.step_history.append("GUARDRAILS")
        logger.info("Executing guardrails workflow step", extra={"workflow_id": state.workflow_id})

        context = GuardrailContext(
            workflow_id=state.workflow_id,
            profile_name="rewrite_strict",
            canonical_resume=state.canonical_resume,
            job_description=state.job_requirements,
        )

        res = await self.guardrails.execute(state.rewritten_resume, context)
        state.guardrail_report = res.model_dump()

        if res.status == GuardrailResultStatus.REJECTED:
            state.status = WorkflowStatus.FAILED
            state.errors.append("Guardrails rejection: " + ", ".join([v.message for v in res.violations]))
            raise GuardrailRejectionError(res)

        if res.repaired_content:
            state.rewritten_resume = res.repaired_content

        return state

    async def run_step_validation(self, state: WorkflowState) -> WorkflowState:
        state.status = WorkflowStatus.VALIDATING
        state.telemetry.step_history.append("VALIDATING")
        logger.info("Executing validation workflow step", extra={"workflow_id": state.workflow_id})
        report = await self.validation_engine.validate(state.rewritten_resume, state.canonical_resume)
        state.validation_report = report.model_dump()
        return state

    async def run_step_ats_analysis(self, state: WorkflowState) -> WorkflowState:
        state.status = WorkflowStatus.ATS_ANALYSIS
        state.telemetry.step_history.append("ATS_ANALYSIS")
        logger.info("Executing ats_analysis workflow step", extra={"workflow_id": state.workflow_id})
        state.ats_report = {
            "score": 92,
            "keyword_coverage": 0.88,
            "recommendations": ["Add LangGraph explicitly to core skills."],
        }
        state.status = WorkflowStatus.COMPLETED
        return state

    async def execute_workflow(self, initial_state: WorkflowState) -> WorkflowState:
        state = initial_state
        state = await self.run_step_parse_resume(state)
        state = await self.run_step_jd_analysis(state)
        state = await self.run_step_retrieval(state)
        state = await self.run_step_planning(state)
        state = await self.run_step_rewrite(state)
        state = await self.run_step_guardrails(state)
        state = await self.run_step_validation(state)
        state = await self.run_step_ats_analysis(state)
        return state
