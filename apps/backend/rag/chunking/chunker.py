import uuid
from domain.resume.models import Resume, Skill, SkillCategory
from domain.shared.vector_store import KnowledgeChunk, ChunkMetadata


class ResumeChunker:
    """Service to decompose a canonical Resume domain model into semantic KnowledgeChunks."""

    def chunk_resume(self, resume: Resume) -> list[KnowledgeChunk]:
        """Segments a canonical Resume into semantic chunks with associated metadata.

        Args:
            resume: The input Resume domain model.

        Returns:
            A list of KnowledgeChunk domain models.
        """
        chunks: list[KnowledgeChunk] = []

        # 1. Summary Chunk
        if resume.summary:
            chunks.append(
                KnowledgeChunk(
                    id=uuid.uuid4(),
                    content=f"Professional Summary:\n{resume.summary}",
                    entity_type="Resume",
                    entity_id=resume.id,
                    metadata=ChunkMetadata(
                        source="resume",
                        importance=0.9,
                        technologies=[],
                        category="Summary",
                        verified=True
                    )
                )
            )

        # 2. Experience Chunks
        for exp in resume.experience:
            bullets_text = "\n".join([f"- {b.text}" for b in exp.bullets])
            content = (
                f"Role: {exp.role}\n"
                f"Company: {exp.company}\n"
                f"Location: {exp.location or 'Unknown'}\n"
                f"Duration: {exp.start_date} - {exp.end_date or 'Present'}\n"
                f"Responsibilities & Accomplishments:\n{bullets_text}"
            )
            chunks.append(
                KnowledgeChunk(
                    id=uuid.uuid4(),
                    content=content,
                    entity_type="Experience",
                    entity_id=exp.id,
                    metadata=ChunkMetadata(
                        source="resume",
                        importance=1.0,
                        technologies=exp.technologies,
                        category="Experience",
                        verified=True
                    )
                )
            )

        # 3. Project Chunks
        for proj in resume.projects:
            bullets_text = "\n".join([f"- {b}" for b in proj.bullets])
            content = (
                f"Project: {proj.title}\n"
                f"Description: {proj.description or ''}\n"
                f"Accomplishments:\n{bullets_text}"
            )
            chunks.append(
                KnowledgeChunk(
                    id=uuid.uuid4(),
                    content=content,
                    entity_type="Project",
                    entity_id=proj.id,
                    metadata=ChunkMetadata(
                        source="resume",
                        importance=0.95,
                        technologies=proj.technologies,
                        category="Project",
                        verified=True
                    )
                )
            )

        # 4. Education Chunks
        for edu in resume.education:
            content = (
                f"Education:\n"
                f"Institution: {edu.institution}\n"
                f"Degree: {edu.degree}\n"
                f"Field of Study: {edu.field or 'General'}\n"
                f"CGPA: {edu.cgpa or 'N/A'}\n"
                f"Dates: {edu.start_date} - {edu.end_date or 'Present'}"
            )
            chunks.append(
                KnowledgeChunk(
                    id=uuid.uuid4(),
                    content=content,
                    entity_type="Education",
                    entity_id=edu.id,
                    metadata=ChunkMetadata(
                        source="resume",
                        importance=0.7,
                        technologies=[],
                        category="Education",
                        verified=True
                    )
                )
            )

        # 5. Skills Chunks (grouped by category)
        skills_by_cat: dict[str, list[Skill]] = {}
        for skill in resume.skills:
            cat_name = "General"
            if skill.category:
                cat_name = skill.category.value if isinstance(skill.category, SkillCategory) else str(skill.category)
            skills_by_cat.setdefault(cat_name, []).append(skill)

        for cat, skills_list in skills_by_cat.items():
            names = [s.name for s in skills_list]
            content = f"Skills ({cat}): " + ", ".join(names)
            chunks.append(
                KnowledgeChunk(
                    id=uuid.uuid4(),
                    content=content,
                    entity_type="Skill",
                    entity_id=resume.id,
                    metadata=ChunkMetadata(
                        source="resume",
                        importance=0.8,
                        technologies=names,
                        category="Skills",
                        verified=True
                    )
                )
            )

        # 6. Certifications Chunks
        for cert in resume.certifications:
            content = (
                f"Certification: {cert.name}\n"
                f"Issuer: {cert.issuer}\n"
                f"Credential ID: {cert.credential_id or 'N/A'}\n"
                f"Issue Date: {cert.issue_date or 'N/A'}"
            )
            chunks.append(
                KnowledgeChunk(
                    id=uuid.uuid4(),
                    content=content,
                    entity_type="Certification",
                    entity_id=cert.id,
                    metadata=ChunkMetadata(
                        source="resume",
                        importance=0.6,
                        technologies=[],
                        category="Certification",
                        verified=True
                    )
                )
            )

        # 7. Achievements Chunks
        for ach in resume.achievements:
            content = (
                f"Achievement: {ach.title}\n"
                f"Category: {ach.category or 'N/A'}\n"
                f"Date: {ach.date or 'N/A'}\n"
                f"Description: {ach.description or ''}"
            )
            chunks.append(
                KnowledgeChunk(
                    id=uuid.uuid4(),
                    content=content,
                    entity_type="Achievement",
                    entity_id=ach.id,
                    metadata=ChunkMetadata(
                        source="resume",
                        importance=0.7,
                        technologies=[],
                        category="Achievement",
                        verified=True
                    )
                )
            )

        return chunks
