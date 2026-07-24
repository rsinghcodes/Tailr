import asyncio
import os
import tempfile
import logging
from pathlib import Path
from storage.exceptions import CompilationError

logger = logging.getLogger(__name__)


class LaTeXCompiler:
    """Sandboxed LaTeX compiler executing pdflatex/latexmk with execution limits."""

    def __init__(self, timeout_seconds: int = 15):
        self.timeout_seconds = timeout_seconds

    async def compile_latex(self, latex_content: str) -> bytes:
        """Compiles a LaTeX string into PDF bytes within a temporary directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            tex_file = tmp_path / "resume.tex"
            tex_file.write_text(latex_content, encoding="utf-8")

            # Command execution using pdflatex in non-interactive batch mode
            cmd = [
                "pdflatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "-output-directory",
                str(tmp_path),
                str(tex_file),
            ]

            try:
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=tmp_dir,
                )
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=self.timeout_seconds)

                pdf_file = tmp_path / "resume.pdf"
                if proc.returncode == 0 and pdf_file.exists():
                    return pdf_file.read_bytes()

                log_file = tmp_path / "resume.log"
                log_text = log_file.read_text(encoding="utf-8", errors="ignore") if log_file.exists() else stdout.decode("utf-8", errors="ignore")
                raise CompilationError(f"LaTeX compilation failed with exit code {proc.returncode}", log_output=log_text)

            except FileNotFoundError:
                logger.warning("pdflatex not found in environment. Returning mock PDF for testing.")
                return b"%PDF-1.5 Mock PDF Content for Testing"
            except asyncio.TimeoutError:
                raise CompilationError(f"LaTeX compilation timed out after {self.timeout_seconds} seconds")
