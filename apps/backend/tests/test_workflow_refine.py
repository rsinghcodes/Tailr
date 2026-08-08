import json

import pytest

from workflows import nodes as workflow_nodes
from workflows.nodes import _format_feedback, rewrite_node
from workflows.state import WorkflowState
from application.workflow.service import WorkflowApplicationService

FEEDBACK_RESUME = {
    "summary": "Backend engineer shipping microservices.",
    "skills": [{"name": "Python"}, {"name": "Django"}],
    "experience": [
        {
            "company": "Acme Corp",
            "role": "Backend Engineer",
            "start_date": "2021-01-01",
            "end_date": "2024-12-31",
            "bullets": [{"text": "Built REST APIs"}],
        }
    ],
    "projects": [],
    "education": [],
}

JOB_REQUIREMENTS = {
    "title": "Senior Backend Engineer",
    "required_skills": ["Python", "Django", "AWS"],
    "preferred_skills": [],
    "responsibilities": [],
    "soft_skills": [],
    "keywords": ["microservices"],
    "experience_level": "Senior",
}

FEEDBACK = {
    "items": [
        {
            "company": "Acme Corp",
            "role": "Backend Engineer",
            "bullet": "Built REST APIs",
            "comment": "Make the impact more specific.",
        }
    ],
    "global_comment": "Keep it under one page.",
}


class RecordingLLM:
    def __init__(self):
        self.prompts: list[str] = []

    async def generate(self, prompt, system_prompt=None, **kwargs):
        self.prompts.append(prompt)
        rewritten = json.loads(json.dumps(FEEDBACK_RESUME))
        rewritten["experience"][0]["bullets"] = [
            {"text": "Designed scalable microservices used by 100k users"},
        ]
        return "```json\n" + json.dumps(rewritten) + "\n```"


class FakeRefineLLM:
    async def generate(self, prompt, system_prompt=None, **kwargs):
        system_prompt = system_prompt or ""
        if "resume strategist" in system_prompt:
            return (
                '```json\n{"target_sections": ["experience"], '
                '"strategy": "Apply user feedback"}\n```'
            )
        if "resume writer" in system_prompt:
            rewritten = json.loads(json.dumps(FEEDBACK_RESUME))
            rewritten["experience"][0]["bullets"] = [
                {"text": "Designed scalable microservices used by 100k users"},
            ]
            return "```json\n" + json.dumps(rewritten) + "\n```"
        if "ATS analyzer" in system_prompt:
            return (
                '```json\n{"score": 85, "keyword_coverage": 0.8, '
                '"strengths": [], "weaknesses": [], "missing_keywords": [], '
                '"recommendations": []}\n```'
            )
        return "{}"


def test_format_feedback_builds_instruction_block():
    block = _format_feedback({"user_feedback": FEEDBACK})
    assert "User Feedback" in block
    assert "Built REST APIs" in block
    assert "(Backend Engineer at Acme Corp)" in block
    assert "Make the impact more specific." in block
    assert "Keep it under one page." in block


def test_format_feedback_returns_empty_when_no_comments():
    assert _format_feedback({}) == ""
    assert _format_feedback(None) == ""
    assert _format_feedback({"user_feedback": None}) == ""
    assert _format_feedback({"user_feedback": {"items": [{"bullet": "x", "comment": ""}]}}) == ""


@pytest.mark.asyncio
async def test_rewrite_node_includes_feedback_in_prompt(monkeypatch):
    llm = RecordingLLM()
    monkeypatch.setattr(workflow_nodes, "_llm", llm)

    state: WorkflowState = {
        "canonical_resume": FEEDBACK_RESUME,
        "rewrite_plan": {"target_sections": ["experience"], "strategy": "Refine"},
        "retrieved_context": "no context",
        "user_feedback": FEEDBACK,
        "telemetry": {"current_step": "REWRITING", "step_history": [], "model_versions": {}},
        "errors": [],
    }

    await rewrite_node(state)
    assert llm.prompts, "rewrite node did not call the LLM"
    prompt = llm.prompts[0]
    assert "User Feedback" in prompt
    assert "modify ONLY the content referenced below" in prompt
    assert "Make the impact more specific." in prompt
    assert "Keep it under one page." in prompt


@pytest.mark.asyncio
async def test_refine_stream_emits_rewritten_resume_and_diff(monkeypatch):
    monkeypatch.setattr(workflow_nodes, "_llm", FakeRefineLLM())

    service = WorkflowApplicationService()
    events = []
    async for event in service.start_workflow_stream(
        canonical_resume=FEEDBACK_RESUME,
        job_requirements=JOB_REQUIREMENTS,
        user_feedback=FEEDBACK,
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
    assert complete
    data = complete[0]["data"]
    assert data["status"] == "completed"
    assert data["rewritten_resume"] is not None
    assert data["bullet_diff"] is not None
    assert data["bullet_diff"]["experience"] != []


LOCK_RESUME = {
    "summary": "Original summary.",
    "skills": [{"name": "Python"}],
    "experience": [
        {
            "company": "Acme Corp",
            "role": "Engineer",
            "start_date": "2020-01-01",
            "end_date": "2022-12-31",
            "bullets": [
                {"text": "Bullet A untouched"},
                {"text": "Bullet B to rewrite"},
            ],
        },
        {
            "company": "Beta Ltd",
            "role": "Developer",
            "start_date": "2019-01-01",
            "end_date": "2020-12-31",
            "bullets": [{"text": "Beta bullet stays"}],
        },
    ],
    "projects": [{"name": "Proj"}],
    "education": [{"degree": "BSc"}],
}

LOCK_FEEDBACK = {
    "items": [
        {
            "company": "Acme Corp",
            "role": "Engineer",
            "bullet": "Bullet B to rewrite",
            "comment": "Make it stronger.",
        }
    ],
    "global_comment": None,
}


class LockLLM:
    async def generate(self, prompt, system_prompt=None, **kwargs):
        rewritten = json.loads(json.dumps(LOCK_RESUME))
        rewritten["summary"] = "Completely new summary."
        rewritten["skills"] = [{"name": "Rust"}]
        rewritten["experience"][0]["bullets"] = [
            {"text": "Bullet A CHANGED"},
            {"text": "Bullet B rewritten with impact"},
        ]
        rewritten["experience"][1]["bullets"] = [{"text": "Beta bullet CHANGED"}]
        rewritten["projects"] = [{"name": "Changed Proj"}]
        rewritten["education"] = [{"degree": "PhD"}]
        return "```json\n" + json.dumps(rewritten) + "\n```"


def _lock_state(feedback):
    return {
        "canonical_resume": LOCK_RESUME,
        "rewrite_plan": {"target_sections": ["experience"], "strategy": "Refine"},
        "retrieved_context": "no context",
        "user_feedback": feedback,
        "telemetry": {"current_step": "REWRITING", "step_history": [], "model_versions": {}},
        "errors": [],
    }


@pytest.mark.asyncio
async def test_rewrite_lock_preserves_uncommented_content(monkeypatch):
    monkeypatch.setattr(workflow_nodes, "_llm", LockLLM())
    result = await rewrite_node(_lock_state(LOCK_FEEDBACK))
    rewritten = result["rewritten_resume"]

    assert rewritten["summary"] == LOCK_RESUME["summary"]
    assert rewritten["skills"] == LOCK_RESUME["skills"]
    assert rewritten["projects"] == LOCK_RESUME["projects"]
    assert rewritten["education"] == LOCK_RESUME["education"]

    acme = next(
        e for e in rewritten["experience"] if e["company"] == "Acme Corp"
    )
    assert [b["text"] for b in acme["bullets"]] == [
        "Bullet A untouched",
        "Bullet B rewritten with impact",
    ]

    beta = next(
        e for e in rewritten["experience"] if e["company"] == "Beta Ltd"
    )
    assert [b["text"] for b in beta["bullets"]] == ["Beta bullet stays"]


@pytest.mark.asyncio
async def test_rewrite_without_feedback_not_locked(monkeypatch):
    monkeypatch.setattr(workflow_nodes, "_llm", LockLLM())
    result = await rewrite_node(_lock_state(None))
    rewritten = result["rewritten_resume"]
    assert rewritten["summary"] == "Completely new summary."
    assert [b["text"] for b in rewritten["experience"][0]["bullets"]] == [
        "Bullet A CHANGED",
        "Bullet B rewritten with impact",
    ]
