import os
from parsers.tokenizer.lexer import LaTeXLexer
from parsers.tokenizer.token_types import TokenType
from parsers.latex.parser import LaTeXParser
from parsers.ast.nodes import CommandNode
from parsers.canonical.analyzer import LaTeXSemanticAnalyzer
from parsers.renderer.latex import LaTeXRenderer
from domain.resume.models import Resume, Skill, SkillCategory


def test_lexer_tokenization():
    source = r"\section{Experience} \resumeItem{Built APIs}"
    lexer = LaTeXLexer(source)
    tokens = lexer.tokenize()

    # Verify key tokens
    # \section is COMMAND
    # { is LBRACE
    # Experience is TEXT
    # } is RBRACE
    assert tokens[0].type == TokenType.COMMAND
    assert tokens[0].value == "\\section"
    assert tokens[1].type == TokenType.LBRACE
    assert tokens[2].type == TokenType.TEXT
    assert tokens[2].value == "Experience"
    assert tokens[3].type == TokenType.RBRACE


def test_parser_ast_generation():
    source = r"\begin{itemize} \item Developed Python scripts \end{itemize}"
    lexer = LaTeXLexer(source)
    tokens = lexer.tokenize()
    
    parser = LaTeXParser(tokens)
    doc = parser.parse()

    # Document should have a flat sequence of commands and text nodes
    commands = [c for c in doc.children if isinstance(c, CommandNode)]
    assert len(commands) == 3
    assert commands[0].name == "begin"
    assert commands[1].name == "item"
    assert commands[2].name == "end"


def test_analyzer_extraction():
    # Read the Jake's Resume fixture
    fixture_path = os.path.join(
        os.path.dirname(__file__), "../../../tests/fixtures/resumes/jakes_resume.tex"
    )
    with open(fixture_path, "r", encoding="utf-8") as f:
        source = f.read()

    lexer = LaTeXLexer(source)
    tokens = lexer.tokenize()
    parser = LaTeXParser(tokens)
    doc = parser.parse()

    analyzer = LaTeXSemanticAnalyzer()
    resume = analyzer.analyze(doc)

    # Verify parsed values match the fixture
    assert resume.metadata.additional_metadata["name"] == "John Doe"
    assert resume.metadata.additional_metadata["email"] == "john.doe@gmail.com"
    assert resume.metadata.additional_metadata["phone"] == "123-456-7890"

    assert len(resume.education) == 1
    assert resume.education[0].institution == "State University"
    assert resume.education[0].degree == "Bachelor of Science in Computer Science"
    assert resume.education[0].start_date == "Aug. 2018"
    assert resume.education[0].end_date == "May 2022"

    assert len(resume.experience) == 1
    assert resume.experience[0].company == "Tech Corp"
    assert resume.experience[0].role == "Software Engineer"
    assert resume.experience[0].location == "San Francisco, CA"
    assert len(resume.experience[0].bullets) == 2
    assert resume.experience[0].bullets[0].text == "Developed scalable backend APIs using Python and FastAPI."

    assert len(resume.projects) == 1
    assert resume.projects[0].title == "Tailr Project"
    assert resume.projects[0].technologies == ["Python", "FastAPI", "Qdrant"]
    assert len(resume.projects[0].bullets) == 1

    assert len(resume.skills) > 0
    languages = [s.name for s in resume.skills if s.category == SkillCategory.PROGRAMMING_LANGUAGE]
    assert "Python" in languages
    assert "Java" in languages


def test_renderer_escaping_and_output():
    resume = Resume(
        summary="A & B Project % 100",
        skills=[
            Skill(name="Python & R", category=SkillCategory.PROGRAMMING_LANGUAGE)
        ]
    )
    renderer = LaTeXRenderer()
    output = renderer.render(resume)

    # Ensure & is escaped to \& and % is escaped to \%
    assert "A \\& B Project \\% 100" in output
    assert "Python \\& R" in output


def test_parser_renderer_roundtrip():
    fixture_path = os.path.join(
        os.path.dirname(__file__), "../../../tests/fixtures/resumes/jakes_resume.tex"
    )
    with open(fixture_path, "r", encoding="utf-8") as f:
        source = f.read()

    # Step 1: Parse and Analyze initial LaTeX
    lexer = LaTeXLexer(source)
    doc = LaTeXParser(lexer.tokenize()).parse()
    resume_1 = LaTeXSemanticAnalyzer().analyze(doc)

    # Step 2: Render back to LaTeX
    renderer = LaTeXRenderer()
    rendered_latex = renderer.render(resume_1)

    # Step 3: Parse and Analyze the rendered LaTeX
    lexer_2 = LaTeXLexer(rendered_latex)
    doc_2 = LaTeXParser(lexer_2.tokenize()).parse()
    resume_2 = LaTeXSemanticAnalyzer().analyze(doc_2)

    # Step 4: Assert equality of the extracted structures
    assert resume_1.metadata.additional_metadata["name"] == resume_2.metadata.additional_metadata["name"]
    assert resume_1.metadata.additional_metadata["email"] == resume_2.metadata.additional_metadata["email"]
    assert len(resume_1.education) == len(resume_2.education)
    assert resume_1.education[0].institution == resume_2.education[0].institution
    assert len(resume_1.experience) == len(resume_2.experience)
    assert resume_1.experience[0].company == resume_2.experience[0].company
    assert len(resume_1.projects) == len(resume_2.projects)
    assert resume_1.projects[0].title == resume_2.projects[0].title
    assert len(resume_1.skills) == len(resume_2.skills)
