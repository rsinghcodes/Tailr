import json
import uuid

import pytest

from workflows import nodes as workflow_nodes
from workflows.graph import get_compiled_graph
from workflows.state import WorkflowState
from application.workflow.service import WorkflowApplicationService

CANONICAL_RESUME = {
    "summary": "Software engineer with 5 years of experience building web applications.",
    "skills": [
        {"name": "Python", "category": "language"},
        {"name": "React", "category": "frontend"},
        {"name": "SQL", "category": "database"},
    ],
    "experience": [
        {
            "company": "Acme Corp",
            "role": "Senior Software Engineer",
            "start_date": "2021-01-01",
            "end_date": "2024-12-31",
            "bullets": [{"text": "Built REST APIs"}, {"text": "Maintained legacy codebase"}],
        }
    ],
    "projects": [
        {
            "title": "Dashboard",
            "description": "Internal analytics dashboard",
            "technologies": ["React"],
        }
    ],
    "education": [
        {
            "institution": "State University",
            "degree": "BS Computer Science",
            "start_date": "2012",
            "end_date": "2016",
        }
    ],
}

JOB_REQUIREMENTS = {
    "title": "Senior Backend Engineer",
    "required_skills": ["Python", "Django", "PostgreSQL", "Kubernetes", "AWS"],
    "preferred_skills": ["FastAPI", "GraphQL"],
    "responsibilities": ["Design scalable microservices", "Lead code reviews"],
    "soft_skills": [],
    "keywords": ["microservices", "distributed systems"],
    "experience_level": "Senior",
}


class FakeLLM:
    """Deterministic fake LLM that emits fenced JSON like real Gemini responses."""

    async def generate(self, prompt, system_prompt=None, **kwargs):
        system_prompt = system_prompt or ""
        if "resume strategist" in system_prompt:
            return (
                '```json\n{"target_sections": ["summary", "experience"], '
                '"strategy": "Quantify impact and match keywords"}\n```'
            )
        if "resume writer" in system_prompt:
            rewritten = json.loads(json.dumps(CANONICAL_RESUME))
            rewritten["summary"] = (
                "Optimized: backend engineer with 5 years of experience shipping "
                "scalable microservices and REST APIs."
            )
            rewritten["experience"][0]["bullets"] = [
                {"text": "Designed and shipped scalable microservices"},
                {"text": "Led code reviews for a team of 6 engineers"},
            ]
            return "```json\n" + json.dumps(rewritten) + "\n```"
        if "ATS analyzer" in system_prompt:
            return (
                '```json\n{"score": 88, "keyword_coverage": 0.85, '
                '"strengths": ["Strong Python experience"], "weaknesses": [], '
                '"missing_keywords": [], "recommendations": ["Add metrics"]}\n```'
            )
        return "{}"


def _initial_state() -> WorkflowState:
    return {
        "request_id": str(uuid.uuid4()),
        "workflow_id": str(uuid.uuid4()),
        "user_id": "test-user",
        "canonical_resume": CANONICAL_RESUME,
        "job_requirements": JOB_REQUIREMENTS,
        "telemetry": {
            "current_step": "NEW",
            "step_history": [],
            "model_versions": {},
        },
        "errors": [],
    }


@pytest.mark.asyncio
async def test_pipeline_produces_optimized_resume(monkeypatch):
    monkeypatch.setattr(workflow_nodes, "_llm", FakeLLM())

    graph = get_compiled_graph()
    final_state = await graph.ainvoke(_initial_state())

    assert final_state.get("rewrite_plan") is not None
    assert final_state["rewrite_plan"].get("target_sections") == ["summary", "experience"]

    rewritten = final_state.get("rewritten_resume")
    assert rewritten is not None
    assert rewritten.get("summary") != CANONICAL_RESUME["summary"]
    assert "Optimized" in rewritten["summary"]
    assert rewritten["experience"][0]["bullets"][0]["text"] != (
        CANONICAL_RESUME["experience"][0]["bullets"][0]["text"]
    )

    ats = final_state.get("ats_report")
    assert ats is not None
    assert ats.get("score") == 88
    assert ats.get("keyword_coverage") == 0.85

    assert final_state.get("validation_report") is not None
    assert final_state.get("guardrail_report") is not None


@pytest.mark.asyncio
async def test_stream_emits_final_state_in_workflow_complete(monkeypatch):
    monkeypatch.setattr(workflow_nodes, "_llm", FakeLLM())

    service = WorkflowApplicationService()
    events = []
    async for event in service.start_workflow_stream(
        canonical_resume=CANONICAL_RESUME,
        job_requirements=JOB_REQUIREMENTS,
    ):
        events.append(event)

    step_names = [e["data"]["step"] for e in events if e["event"] == "step_complete"]
    assert step_names == [
        "retrieve_context",
        "plan",
        "rewrite",
        "guardrails",
        "validation",
        "ats_analysis",
        "render",
    ]

    complete = [e for e in events if e["event"] == "workflow_complete"]
    assert complete, "workflow_complete event was not emitted"
    data = complete[0]["data"]
    assert data["workflow_id"]
    assert data["status"] == "completed"
    assert data["rewritten_resume"] is not None
    assert data["ats_report"] is not None
    assert data["guardrail_report"] is not None
    assert data["validation_report"] is not None
    assert data["rewrite_plan"] is not None
