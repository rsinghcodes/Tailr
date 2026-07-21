import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from domain.workflow.models import WorkflowState, WorkflowStatus
from domain.workflow.repository import WorkflowRepository
from domain.job_description.models import JobDescription
from domain.evaluation.models import ValidationResult
from domain.ats.models import ATSReport
from infrastructure.database.workflow_models import WorkflowRunModel
from infrastructure.database.job_description_models import JobDescriptionModel
from infrastructure.database.resume_models import ResumeVersionModel
from infrastructure.repositories.resume_repository import ResumeRepositoryImpl


class WorkflowRepositoryImpl(WorkflowRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.resume_repo = ResumeRepositoryImpl(session)

    async def get_by_id(self, workflow_id: uuid.UUID) -> Optional[WorkflowState]:
        stmt = select(WorkflowRunModel).where(WorkflowRunModel.id == workflow_id)
        result = await self.session.execute(stmt)
        db_run = result.scalar_one_or_none()
        if not db_run:
            return None
        return await self._to_domain(db_run)

    async def save(self, state: WorkflowState) -> WorkflowState:
        # 1. Persist/Resolve Job Description
        db_jd_id = None
        if state.job_description:
            stmt_jd = select(JobDescriptionModel).where(JobDescriptionModel.id == state.job_description.id)
            res_jd = await self.session.execute(stmt_jd)
            db_jd = res_jd.scalar_one_or_none()

            if not db_jd:
                db_jd = JobDescriptionModel(
                    id=state.job_description.id,
                    company=state.job_description.company or "Unknown",
                    title=state.job_description.title,
                    description=state.job_description.description,
                    parsed_requirements=None
                )
                self.session.add(db_jd)
                await self.session.flush()
            else:
                db_jd.company = state.job_description.company or "Unknown"
                db_jd.title = state.job_description.title
                db_jd.description = state.job_description.description
            db_jd_id = db_jd.id

        # 2. Persist/Resolve Original Resume
        db_resume_container_id = None
        if state.resume:
            # Check if version exists
            stmt_v = select(ResumeVersionModel).where(ResumeVersionModel.id == state.resume.id)
            res_v = await self.session.execute(stmt_v)
            db_version = res_v.scalar_one_or_none()

            if not db_version:
                # Save it via resume repo
                await self.resume_repo.save(state.resume)
                # fetch it again to get its container ID
                stmt_v2 = select(ResumeVersionModel).where(ResumeVersionModel.id == state.resume.id)
                res_v2 = await self.session.execute(stmt_v2)
                db_version = res_v2.scalar_one_or_none()

            if db_version:
                db_resume_container_id = db_version.resume_id

        # 3. Persist/Resolve Optimized Resume
        _db_opt_resume_container_id = None
        if state.rewritten_resume:
            stmt_ov = select(ResumeVersionModel).where(ResumeVersionModel.id == state.rewritten_resume.id)
            res_ov = await self.session.execute(stmt_ov)
            db_opt_version = res_ov.scalar_one_or_none()

            if not db_opt_version:
                # Save it under the same container id if we have one
                await self.resume_repo.save(
                    state.rewritten_resume,
                    resume_container_id=db_resume_container_id
                )
                # fetch container details
                stmt_ov2 = select(ResumeVersionModel).where(ResumeVersionModel.id == state.rewritten_resume.id)
                res_ov2 = await self.session.execute(stmt_ov2)
                db_opt_version = res_ov2.scalar_one_or_none()

            if db_opt_version:
                _db_opt_resume_container_id = db_opt_version.resume_id

        # 4. Serialize other workflow elements into state_data
        state_data = {
            "retrieved_context": state.retrieved_context,
            "rewrite_plan": state.rewrite_plan,
            "validation_report": state.validation_report.model_dump(mode="json") if state.validation_report else None,
            "ats_report": state.ats_report.model_dump(mode="json") if state.ats_report else None
        }

        # 5. Persist/Update WorkflowRunModel
        stmt_w = select(WorkflowRunModel).where(WorkflowRunModel.id == state.id)
        res_w = await self.session.execute(stmt_w)
        db_run = res_w.scalar_one_or_none()

        if db_run:
            db_run.status = state.status.value
            db_run.resume_id = db_resume_container_id
            db_run.job_description_id = db_jd_id
            db_run.state_data = state_data
            db_run.completed_at = datetime.utcnow() if state.status in (WorkflowStatus.COMPLETED, WorkflowStatus.FAILED) else None
            db_run.updated_at = datetime.utcnow()
        else:
            db_run = WorkflowRunModel(
                id=state.id,
                resume_id=db_resume_container_id,
                job_description_id=db_jd_id,
                status=state.status.value,
                current_step=None,
                started_at=state.created_at,
                completed_at=datetime.utcnow() if state.status in (WorkflowStatus.COMPLETED, WorkflowStatus.FAILED) else None,
                token_usage=None,
                latency_ms=None,
                state_data=state_data
            )
            db_run.created_at = state.created_at
            db_run.updated_at = state.updated_at
            self.session.add(db_run)

        await self.session.commit()
        return state

    async def delete(self, workflow_id: uuid.UUID) -> bool:
        stmt = select(WorkflowRunModel).where(WorkflowRunModel.id == workflow_id)
        result = await self.session.execute(stmt)
        db_run = result.scalar_one_or_none()
        if not db_run:
            return False
        
        await self.session.delete(db_run)
        await self.session.commit()
        return True

    async def _to_domain(self, db_run: WorkflowRunModel) -> WorkflowState:
        # Load associated models
        # Fetch original resume from version
        resume = None
        if db_run.resume_id:
            # Get latest version in container
            stmt_v = select(ResumeVersionModel).where(ResumeVersionModel.resume_id == db_run.resume_id).order_by(ResumeVersionModel.version.desc()).limit(1)
            res_v = await self.session.execute(stmt_v)
            db_v = res_v.scalar_one_or_none()
            if db_v:
                resume = self.resume_repo._to_domain(db_v)

        # Fetch optimized resume
        rewritten_resume = None
        # We can look up the specific optimized container, or fetch by ID if stored in state_data or versions table
        # If there is a linked optimized resume container, fetch its latest version
        if db_run.job_description_id:  # Fetch JD details if linked
            stmt_jd = select(JobDescriptionModel).where(JobDescriptionModel.id == db_run.job_description_id)
            res_jd = await self.session.execute(stmt_jd)
            db_jd = res_jd.scalar_one_or_none()
            job_description = JobDescription(
                id=db_jd.id,
                title=db_jd.title,
                company=db_jd.company,
                description=db_jd.description
            ) if db_jd else None
        else:
            job_description = None

        state_data = db_run.state_data or {}
        
        # Load optimized resume version
        # If state_data has a custom key, or we just look up the latest version on the optimized resume container
        if db_run.resume_id:  # If we have a container, try to find the rewritten version
            # Usually, original version is 1, rewritten is 2+ in the same container.
            # So let's look for version 2+ or look up the optimized resume container
            # In our database schema we have optimized_resume_id (which is not physically in the schema of Database-Design.md, but let's check!
            # Ah, Database-Design.md lists workflow_runs with only: id, resume_id, job_description_id, status, current_step, started_at, completed_at, token_usage, latency_ms.
            # So the optimized resume version is usually just another version in the same resume container!)
            # So let's fetch version 2 of the container for rewritten_resume if it exists.
            stmt_ov = select(ResumeVersionModel).where(ResumeVersionModel.resume_id == db_run.resume_id, ResumeVersionModel.version > 1).order_by(ResumeVersionModel.version.desc()).limit(1)
            res_ov = await self.session.execute(stmt_ov)
            db_ov = res_ov.scalar_one_or_none()
            if db_ov:
                rewritten_resume = self.resume_repo._to_domain(db_ov)

        # Deserialize reports
        val_rep_data = state_data.get("validation_report")
        validation_report = ValidationResult(**val_rep_data) if val_rep_data else None

        ats_rep_data = state_data.get("ats_report")
        ats_report = ATSReport(**ats_rep_data) if ats_rep_data else None

        state = WorkflowState(
            id=db_run.id,
            status=WorkflowStatus(db_run.status),
            resume=resume,
            job_description=job_description,
            retrieved_context=state_data.get("retrieved_context", []),
            rewrite_plan=state_data.get("rewrite_plan"),
            rewritten_resume=rewritten_resume,
            validation_report=validation_report,
            ats_report=ats_report,
            created_at=db_run.created_at,
            updated_at=db_run.updated_at,
            version=1
        )
        return state
