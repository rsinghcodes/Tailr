import pytest
from unittest.mock import AsyncMock, MagicMock
from domain.resume.models import Resume
from domain.job_description.models import JobRequirements
from domain.shared.llm_provider import LLMProvider
from prompts.registry import PromptRegistry

from agents.planner.agent import PlannerAgent, PlannerOutput, PlanItem
from agents.rewriter.agent import RewriterAgent
from agents.ats.agent import ATSAdvisorAgent, ATSReport


@pytest.fixture
def mock_registry():
    registry = MagicMock(spec=PromptRegistry)
    registry.get_prompt.side_effect = lambda cat, name, ver="v1": {
        ("planner", "system"): "Planner System Prompt",
        ("planner", "user"): "Planner User Prompt {resume_json} {job_requirements} {retrieved_context}",
        ("rewrite", "system"): "Rewrite System Prompt",
        ("rewrite", "user"): "Rewrite User Prompt {resume_json} {rewrite_plan} {retrieved_context}",
        ("ats", "system"): "ATS System Prompt",
        ("ats", "user"): "ATS User Prompt {original_resume} {optimized_resume} {job_requirements}",
    }[(cat, name)]
    return registry


@pytest.mark.asyncio
async def test_planner_agent(mock_registry):
    mock_llm = MagicMock(spec=LLMProvider)
    expected_output = PlannerOutput(
        summary=[PlanItem(action="modify", instructions="Add Python keyword", reasoning="Required in JD")],
        skills=[PlanItem(action="add", instructions="Add FastAPI", reasoning="In JD")]
    )
    mock_llm.generate = AsyncMock(return_value=expected_output)

    agent = PlannerAgent(mock_llm, mock_registry)
    resume = Resume(summary="Developer")
    reqs = JobRequirements(required_skills=["Python"])
    context = ["Retrieved background chunk 1"]

    plan = await agent.plan(resume, reqs, context)

    assert plan == expected_output
    assert plan.summary[0].action == "modify"
    assert plan.skills[0].action == "add"
    mock_llm.generate.assert_called_once()


@pytest.mark.asyncio
async def test_rewriter_agent(mock_registry):
    mock_llm = MagicMock(spec=LLMProvider)
    expected_resume = Resume(summary="Rewritten developer summary")
    mock_llm.generate = AsyncMock(return_value=expected_resume)

    agent = RewriterAgent(mock_llm, mock_registry)
    resume = Resume(summary="Developer")
    plan = PlannerOutput()
    context = ["Context"]

    result = await agent.rewrite(resume, plan, context)

    assert result == expected_resume
    assert result.summary == "Rewritten developer summary"
    mock_llm.generate.assert_called_once()


@pytest.mark.asyncio
async def test_ats_advisor_agent(mock_registry):
    mock_llm = MagicMock(spec=LLMProvider)
    expected_report = ATSReport(
        score=95,
        strengths=["Python keyword added"],
        weaknesses=[],
        recommendations=[]
    )
    mock_llm.generate = AsyncMock(return_value=expected_report)

    agent = ATSAdvisorAgent(mock_llm, mock_registry)
    orig_resume = Resume(summary="Developer")
    opt_resume = Resume(summary="Optimized")
    reqs = JobRequirements(required_skills=["Python"])

    report = await agent.analyze(orig_resume, opt_resume, reqs)

    assert report == expected_report
    assert report.score == 95
    assert len(report.strengths) == 1
    mock_llm.generate.assert_called_once()
