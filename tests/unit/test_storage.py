import pytest
from pathlib import Path
from storage.local import LocalStorageProvider
from storage.exceptions import FileNotFoundStorageError, InvalidPathError
from storage.compiler import LaTeXCompiler


@pytest.mark.asyncio
async def test_local_storage_save_and_read(tmp_path):
    provider = LocalStorageProvider(root_dir=tmp_path)

    relative_path = "resumes/test_resume.tex"
    content = "\\section{Education}"

    saved_path = await provider.save_file(relative_path, content)
    assert Path(saved_path).exists()

    read_back = await provider.read_file(relative_path)
    assert read_back.decode("utf-8") == content


@pytest.mark.asyncio
async def test_local_storage_path_traversal_prevention(tmp_path):
    provider = LocalStorageProvider(root_dir=tmp_path)

    with pytest.raises(InvalidPathError):
        await provider.save_file("../../../etc/passwd", "malicious content")


@pytest.mark.asyncio
async def test_latex_compiler():
    compiler = LaTeXCompiler(timeout_seconds=5)
    latex_src = r"\documentclass{article}\begin{document}Hello World\end{document}"

    pdf_bytes = await compiler.compile_latex(latex_src)
    assert pdf_bytes.startswith(b"%PDF")
