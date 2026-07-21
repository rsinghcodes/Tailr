import pytest
import pytest_asyncio
from sqlalchemy import select
from infrastructure.database.session import SessionFactory
from infrastructure.database.engine import engine
from domain.resume.models import Resume, Skill, SkillCategory
from domain.job_description.models import JobDescription
from domain.workflow.models import WorkflowState, WorkflowStatus
from domain.evaluation.models import ValidationResult
from domain.ats.models import ATSReport
from infrastructure.repositories.resume_repository import ResumeRepositoryImpl
from infrastructure.repositories.workflow_repository import WorkflowRepositoryImpl
from infrastructure.database.resume_models import ResumeVersionModel
from infrastructure.database.job_description_models import JobDescriptionModel


@pytest_asyncio.fixture(autouse=True)
async def dispose_db_engine():
    yield
    # Clean up connection pool while the loop is active
    await engine.dispose()


@pytest.mark.asyncio
async def test_resume_repository_crud():
    async with SessionFactory() as session:
        resume_repo = ResumeRepositoryImpl(session)

        # 1. Create a dummy Resume
        resume = Resume(
            summary="Backend Engineer with Python expertise",
            skills=[
                Skill(name="Python", category=SkillCategory.PROGRAMMING_LANGUAGE),
                Skill(name="PostgreSQL", category=SkillCategory.DATABASE)
            ]
        )

        try:
            # Save it
            saved_resume = await resume_repo.save(resume, raw_latex="% dummy latex", title="My Resume")
            assert saved_resume.id == resume.id

            # Retrieve it
            retrieved = await resume_repo.get_by_version_id(resume.id)
            assert retrieved is not None
            assert retrieved.summary == resume.summary
            assert len(retrieved.skills) == 2
            assert retrieved.skills[0].name == "Python"

            # 2. Update Resume
            resume.summary = "Updated summary"
            await resume_repo.save(resume, raw_latex="% updated latex")
            
            retrieved_updated = await resume_repo.get_by_version_id(resume.id)
            assert retrieved_updated is not None
            assert retrieved_updated.summary == "Updated summary"

        finally:
            # Clean up the DB
            stmt = select(ResumeVersionModel).where(ResumeVersionModel.id == resume.id)
            result = await session.execute(stmt)
            db_version = result.scalar_one_or_none()
            if db_version:
                container_id = db_version.resume_id
                await resume_repo.delete(container_id)


@pytest.mark.asyncio
async def test_workflow_repository_crud():
    async with SessionFactory() as session:
        workflow_repo = WorkflowRepositoryImpl(session)
        resume_repo = ResumeRepositoryImpl(session)

        # 1. Create original resume
        resume = Resume(
            summary="Original Resume summary",
            skills=[]
        )
        
        # Create job description
        jd = JobDescription(
            title="FastAPI Developer",
            company="Tech Innovators",
            description="Required: FastAPI expertise."
        )

        # Create workflow state
        state = WorkflowState(
            resume=resume,
            job_description=jd,
            status=WorkflowStatus.PLANNING,
            retrieved_context=["Context item 1"],
            rewrite_plan="Plan wording",
            validation_report=ValidationResult(
                passed=True,
                errors=[],
                hallucination_score=0.1
            ),
            ats_report=ATSReport(
                overall_score=80.0,
                keyword_coverage=0.6,
                missing_keywords=["Docker"],
                strengths=["Good backend background"],
                weaknesses=[],
                recommendations=[]
            )
        )

        try:
            # Save workflow run
            saved_state = await workflow_repo.save(state)
            assert saved_state.id == state.id

            # Retrieve workflow run
            retrieved_state = await workflow_repo.get_by_id(state.id)
            assert retrieved_state is not None
            assert retrieved_state.status == WorkflowStatus.PLANNING
            assert retrieved_state.resume is not None
            assert retrieved_state.resume.summary == "Original Resume summary"
            assert retrieved_state.job_description is not None
            assert retrieved_state.job_description.company == "Tech Innovators"
            assert retrieved_state.ats_report is not None
            assert retrieved_state.ats_report.overall_score == 80.0

            # 2. Update status and save
            state.status = WorkflowStatus.COMPLETED
            await workflow_repo.save(state)

            retrieved_completed = await workflow_repo.get_by_id(state.id)
            assert retrieved_completed is not None
            assert retrieved_completed.status == WorkflowStatus.COMPLETED

        finally:
            # Clean up the DB
            await workflow_repo.delete(state.id)
            
            # Delete JDs
            stmt_jd = select(JobDescriptionModel).where(JobDescriptionModel.id == jd.id)
            res_jd = await session.execute(stmt_jd)
            db_jd = res_jd.scalar_one_or_none()
            if db_jd:
                await session.delete(db_jd)
                await session.commit()
                
            # Delete Resumes
            stmt_v = select(ResumeVersionModel).where(ResumeVersionModel.id == resume.id)
            res_v = await session.execute(stmt_v)
            db_version = res_v.scalar_one_or_none()
            if db_version:
                await resume_repo.delete(db_version.resume_id)
