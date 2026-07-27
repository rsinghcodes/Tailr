import logging
from workflows.state import WorkflowState, WorkflowStatus
from guardrails.pipeline import GuardrailsEngine
from guardrails.base import GuardrailContext, GuardrailResultStatus
from guardrails.exceptions import GuardrailRejectionError
from validators.engine import ValidationEngine
from agents.jd_analyzer.agent import JDAnalyzerAgent
from agents.planner.agent import PlannerAgent
from agents.rewriter.agent import RewriterAgent
from agents.ats.agent import ATSAdvisorAgent
from infrastructure.ollama.llm_provider import OllamaProvider
from infrastructure.ollama.embedding_provider import OllamaEmbeddingProvider
from infrastructure.qdrant.vector_store import QdrantVectorStore
from parsers.document.factory import DocumentParserFactory
from config.settings import settings

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """LangGraph-aligned event-driven workflow engine orchestrating AI agents, guardrails, and validation."""

    def __init__(
        self,
        guardrails_engine: GuardrailsEngine | None = None,
        validation_engine: ValidationEngine | None = None,
        llm_provider: OllamaProvider | None = None,
        embedding_provider: OllamaEmbeddingProvider | None = None,
        vector_store: QdrantVectorStore | None = None,
    ):
        self.guardrails = guardrails_engine or GuardrailsEngine()
        self.validation_engine = validation_engine or ValidationEngine()
        self.llm_provider = llm_provider or OllamaProvider(base_url=settings.OLLAMA_URL)
        self.embedding_provider = embedding_provider or OllamaEmbeddingProvider(base_url=settings.OLLAMA_URL)
        self.vector_store = vector_store or QdrantVectorStore()

        self.parser_factory = DocumentParserFactory()
        self.jd_analyzer = JDAnalyzerAgent(self.llm_provider)
        self.planner = PlannerAgent(self.llm_provider)
        self.rewriter = RewriterAgent(self.llm_provider)
        self.ats_advisor = ATSAdvisorAgent(self.llm_provider)

    async def run_step_parse_resume(self, state: WorkflowState) -> WorkflowState:
        state.status = WorkflowStatus.PARSING
        state.telemetry.step_history.append("PARSING")
        logger.info("Executing parse_resume workflow step", extra={"workflow_id": state.workflow_id})

        if state.raw_resume_text:
            try:
                from parsers.tokenizer.lexer import LaTeXLexer
                from parsers.latex.parser import LaTeXParser
                from parsers.canonical.analyzer import LaTeXSemanticAnalyzer

                lexer = LaTeXLexer(state.raw_resume_text)
                tokens = lexer.tokenize()
                parser = LaTeXParser(tokens)
                doc = parser.parse()
                analyzer = LaTeXSemanticAnalyzer()
                resume = analyzer.analyze(doc)
                state.canonical_resume = resume.model_dump(mode="json")
            except Exception as exc:
                logger.warning("LaTeX parser failed, using text extraction fallback: %s", str(exc))
                state.canonical_resume = {
                    "summary": state.raw_resume_text[:500],
                    "skills": [],
                    "experience": [],
                    "projects": [],
                    "education": [],
                }
        return state

    async def run_step_jd_analysis(self, state: WorkflowState) -> WorkflowState:
        state.status = WorkflowStatus.JD_ANALYSIS
        state.telemetry.step_history.append("JD_ANALYSIS")
        logger.info("Executing analyze_jd workflow step", extra={"workflow_id": state.workflow_id})

        if state.job_description_text:
            jd_output = await self.jd_analyzer.analyze(state.job_description_text)
            state.job_requirements = jd_output.model_dump()
        else:
            state.job_requirements = {
                "required_skills": ["Python", "FastAPI", "Docker", "LangGraph"],
                "preferred_skills": ["PostgreSQL", "Qdrant", "Redis"],
                "seniority": "Mid-Senior",
                "domain": "AI Platform Engineering",
                "priority_keywords": ["RAG", "FastAPI", "Python", "Microservices"],
                "responsibilities": ["Build scalable APIs and agentic workflows."],
            }
        return state

    async def run_step_retrieval(self, state: WorkflowState) -> WorkflowState:
        state.status = WorkflowStatus.RETRIEVAL
        state.telemetry.step_history.append("RETRIEVAL")
        logger.info("Executing retrieve_context workflow step", extra={"workflow_id": state.workflow_id})

        keywords = state.job_requirements.get("priority_keywords", []) or ["Python", "FastAPI"]
        query_text = " ".join(keywords)

        try:
            query_vector = await self.embedding_provider.get_embedding(query_text)
            hits = await self.vector_store.search(collection_name="resume_chunks", query_vector=query_vector, limit=3)
            if hits:
                retrieved = "\n".join([str(h.payload) for h in hits])
                state.retrieved_context = retrieved
            else:
                state.retrieved_context = f"Retrieved candidate experience matching keywords: {', '.join(keywords)}"
        except Exception as exc:
            logger.warning("Vector search retrieval warning, using text fallback: %s", str(exc))
            state.retrieved_context = f"Retrieved candidate context for keywords: {', '.join(keywords)}"

        return state

    async def run_step_planning(self, state: WorkflowState) -> WorkflowState:
        state.status = WorkflowStatus.PLANNING
        state.telemetry.step_history.append("PLANNING")
        logger.info("Executing planning workflow step", extra={"workflow_id": state.workflow_id})

        plan_output = await self.planner.plan(
            canonical_resume=state.canonical_resume,
            jd_requirements=state.job_requirements,
            context=state.retrieved_context,
            model="qwen3:8b",
        )
        state.rewrite_plan = plan_output.model_dump()
        return state

    async def run_step_rewrite(self, state: WorkflowState) -> WorkflowState:
        state.status = WorkflowStatus.REWRITING
        state.telemetry.step_history.append("REWRITING")
        logger.info("Executing rewrite workflow step", extra={"workflow_id": state.workflow_id})

        rewritten_res = await self.rewriter.rewrite(
            resume=state.canonical_resume,
            rewrite_plan=state.rewrite_plan,
            retrieved_context=state.retrieved_context,
            model="qwen3:8b",
        )
        rewritten_dict = rewritten_res.model_dump()

        # Flatten ExperienceBullet objects to simple strings for frontend
        if "experience" in rewritten_dict:
            for exp in rewritten_dict["experience"]:
                if "bullets" in exp:
                    exp["bullets"] = [
                        b["text"] if isinstance(b, dict) and "text" in b else str(b)
                        for b in exp["bullets"]
                    ]

        state.rewritten_resume = rewritten_dict
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

        ats_report = await self.ats_advisor.analyze(
            original_resume=state.canonical_resume,
            optimized_resume=state.rewritten_resume,
            job_requirements=state.job_requirements,
            model="qwen3:8b",
        )
        state.ats_report = ats_report.model_dump()
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
