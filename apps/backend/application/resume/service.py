import uuid
from typing import Optional
from domain.resume.models import Resume
from domain.resume.repository import ResumeRepository
from parsers.tokenizer.lexer import LaTeXLexer
from parsers.latex.parser import LaTeXParser
from parsers.canonical.analyzer import LaTeXSemanticAnalyzer


class ResumeService:
    """Application service to manage resume parsing, creation, updating, versioning, listing, and deletion."""

    def __init__(self, repository: ResumeRepository):
        """Initializes the resume service.

        Args:
            repository: The resume repository port.
        """
        self.repository = repository

    async def upload_resume(
        self,
        raw_latex: str,
        filename: str,
        title: Optional[str] = None,
        resume_container_id: Optional[uuid.UUID] = None,
    ) -> Resume:
        """Parses LaTeX content, builds a Canonical Resume Model, and persists it.

        Args:
            raw_latex: The raw LaTeX text content of the resume.
            filename: The original uploaded file name.
            title: An optional title for the resume.
            resume_container_id: An optional ID of an existing resume container to add a new version to.

        Returns:
            The parsed domain Resume entity.
        """
        # Run compiler-style parsing pipeline
        lexer = LaTeXLexer(raw_latex)
        tokens = lexer.tokenize()
        parser = LaTeXParser(tokens)
        doc = parser.parse()

        analyzer = LaTeXSemanticAnalyzer()
        resume = analyzer.analyze(doc)

        # Explicitly update template name metadata from filename or parsed name
        resume.metadata.template_name = filename
        if title:
            resume.metadata.additional_metadata["custom_title"] = title

        # Save to repository
        await self.repository.save(
            resume=resume,
            raw_latex=raw_latex,
            title=title,
            resume_container_id=resume_container_id,
        )
        return resume

    async def get_resume_by_version(self, version_id: uuid.UUID) -> Optional[Resume]:
        """Retrieves a specific resume version.

        Args:
            version_id: The unique ID of the resume version.

        Returns:
            The domain Resume entity if found, else None.
        """
        return await self.repository.get_by_version_id(version_id)

    async def list_resumes(self) -> list[dict]:
        """Lists all parent resume containers.

        Returns:
            A list of dictionary records summarizing each resume.
        """
        raw_list = await self.repository.list_all()
        return [
            {
                "id": item[0],
                "title": item[1],
                "current_version": item[2],
                "status": item[3],
                "created_at": item[4],
                "updated_at": item[5],
            }
            for item in raw_list
        ]

    async def get_resume_versions(self, resume_id: uuid.UUID) -> list[dict]:
        """Retrieves all version records for a specific resume container.

        Args:
            resume_id: The unique ID of the parent resume container.

        Returns:
            A list of dictionary records representing each version.
        """
        raw_list = await self.repository.get_versions_by_resume_id(resume_id)
        return [
            {
                "version_id": item[0],
                "version": item[1],
                "latex_path": item[2],
                "created_at": item[3],
                "updated_at": item[4],
            }
            for item in raw_list
        ]

    async def delete_resume_container(self, resume_id: uuid.UUID) -> bool:
        """Deletes a parent resume container and all its versions.

        Args:
            resume_id: The unique ID of the resume container.

        Returns:
            True if deletion was successful, else False.
        """
        return await self.repository.delete(resume_id)
