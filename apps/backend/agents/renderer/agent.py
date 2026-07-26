import logging
from typing import Any
from domain.resume.models import Resume, ExperienceBullet, Skill

logger = logging.getLogger(__name__)


class LaTeXRendererAgent:
    """Agent responsible for rendering a Canonical Resume Model into compile-ready LaTeX code."""

    def render(self, resume: Resume | dict[str, Any], template_name: str = "classic") -> str:
        if isinstance(resume, dict):
            try:
                res_obj = Resume.model_validate(resume)
            except Exception as exc:
                logger.warning("Resume validation warning in LaTeXRendererAgent: %s", str(exc))
                res_obj = Resume(summary=resume.get("summary", "Software Engineer"))
        else:
            res_obj = resume

        header_name = getattr(res_obj.metadata, "template_name", None) or "Candidate Name"
        header_email = "candidate@tailr.ai"

        latex_lines = [
            r"\documentclass[letterpaper,11pt]{article}",
            r"\usepackage[utf8]{inputenc}",
            r"\usepackage[margin=0.75in]{geometry}",
            r"\usepackage{hyperref}",
            r"\begin{document}",
            r"\pagestyle{empty}",
            rf"\centerline{{\Huge \bfseries {header_name}}}",
            rf"\centerline{{{header_email}}}",
            r"\vspace{10pt}",
            r"\hrule",
            r"\vspace{10pt}",
        ]

        if res_obj.summary:
            latex_lines.extend([
                r"\section*{Professional Summary}",
                res_obj.summary,
                r"\vspace{8pt}",
            ])

        if res_obj.experience:
            latex_lines.append(r"\section*{Work Experience}")
            for exp in res_obj.experience:
                company = exp.company or "Company"
                role = exp.role or "Role"
                start = exp.start_date or ""
                end = exp.end_date or "Present"
                latex_lines.append(rf"\noindent \textbf{{{role}}} --- \textit{{{company}}} \hfill {{{start}}} - {{{end}}}")
                if exp.bullets:
                    latex_lines.append(r"\begin{itemize}")
                    for b in exp.bullets:
                        text_content = b.text if isinstance(b, ExperienceBullet) else str(b)
                        clean_b = text_content.replace("%", r"\%").replace("$", r"\$").replace("&", r"\&")
                        latex_lines.append(rf"  \item {clean_b}")
                    latex_lines.append(r"\end{itemize}")
                latex_lines.append(r"\vspace{6pt}")

        if res_obj.skills:
            latex_lines.append(r"\section*{Skills}")
            sk_names = [s.name if isinstance(s, Skill) else str(s) for s in res_obj.skills]
            clean_skills = ", ".join(sk_names).replace("%", r"\%").replace("$", r"\$").replace("&", r"\&")
            latex_lines.append(rf"\noindent \textbf{{Technical Skills}}: {clean_skills}\\")

        latex_lines.append(r"\end{document}")
        return "\n".join(latex_lines)
