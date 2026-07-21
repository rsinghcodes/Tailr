from domain.resume.models import Resume, Experience, Project, Skill, Education, SkillCategory
from domain.job_description.models import JobDescription, JobRequirements
from domain.ats.models import ATSReport
from domain.evaluation.models import ValidationResult, ValidationIssue, Severity
from domain.workflow.models import WorkflowState, WorkflowStatus


def test_resume_model_validation():
    # Verify we can instantiate the resume model with dummy data
    resume = Resume(
        summary="Experienced engineer",
        skills=[
            Skill(name="Python", category=SkillCategory.PROGRAMMING_LANGUAGE),
            Skill(name="FastAPI", category=SkillCategory.FRAMEWORK)
        ],
        experience=[
            Experience(
                company="Tech Corp",
                role="Engineer",
                start_date="2020",
                bullets=[]
            )
        ],
        projects=[
            Project(
                title="Tailr",
                technologies=["Python", "FastAPI"]
            )
        ],
        education=[
            Education(
                institution="University",
                degree="BS",
                start_date="2016",
                end_date="2020"
            )
        ]
    )

    assert resume.summary == "Experienced engineer"
    assert len(resume.skills) == 2
    assert resume.skills[0].name == "Python"
    assert resume.skills[0].category == SkillCategory.PROGRAMMING_LANGUAGE
    assert len(resume.experience) == 1
    assert resume.experience[0].company == "Tech Corp"
    assert len(resume.projects) == 1
    assert resume.projects[0].title == "Tailr"
    assert resume.projects[0].technologies == ["Python", "FastAPI"]
    assert len(resume.education) == 1
    assert resume.education[0].institution == "University"


def test_job_description_model_validation():
    jd = JobDescription(
        title="Software Engineer",
        company="Google",
        description="Looking for an engineer."
    )
    reqs = JobRequirements(
        required_skills=["Python", "Go"],
        preferred_skills=["Docker"],
        experience_level="Senior"
    )
    assert jd.title == "Software Engineer"
    assert jd.company == "Google"
    assert reqs.required_skills == ["Python", "Go"]
    assert reqs.experience_level == "Senior"


def test_ats_report_validation():
    report = ATSReport(
        overall_score=85.0,
        keyword_coverage=0.75,
        missing_keywords=["Kubernetes"],
        strengths=["Strong Python backend experience"],
        weaknesses=["Missing containerization tools"],
        recommendations=["Add Docker/Kubernetes keywords"]
    )
    assert report.overall_score == 85.0
    assert report.keyword_coverage == 0.75
    assert "Kubernetes" in report.missing_keywords


def test_evaluation_validation():
    issue = ValidationIssue(
        type="hallucination",
        severity=Severity.ERROR,
        message="Invented job title",
        section="Experience"
    )
    result = ValidationResult(
        passed=False,
        errors=[issue],
        hallucination_score=0.9
    )
    assert not result.passed
    assert len(result.errors) == 1
    assert result.errors[0].severity == Severity.ERROR
    assert result.hallucination_score == 0.9


def test_workflow_validation():
    state = WorkflowState(
        status=WorkflowStatus.PENDING
    )
    assert state.status == WorkflowStatus.PENDING
    assert state.resume is None
    assert len(state.retrieved_context) == 0
