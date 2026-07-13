from domain.resume.models import Resume


class LaTeXRenderer:
    def escape(self, text: str) -> str:
        if not text:
            return ""
        # Characters that must be escaped in LaTeX
        chars = {
            "&": "\\&",
            "%": "\\%",
            "$": "\\$",
            "#": "\\#",
            "_": "\\_",
            "{": "\\{",
            "}": "\\}",
            "~": "\\textasciitilde{}",
            "^": "\\textasciicircum{}",
        }
        res = ""
        for char in text:
            res += chars.get(char, char)
        return res

    def render(self, resume: Resume) -> str:
        metadata = resume.metadata.additional_metadata
        name = self.escape(metadata.get("name", "Candidate Name"))
        email = self.escape(metadata.get("email", ""))
        phone = self.escape(metadata.get("phone", ""))
        linkedin = self.escape(metadata.get("linkedin", ""))
        github = self.escape(metadata.get("github", ""))

        latex = []
        
        # Preamble setup (Jake's Resume style)
        latex.append(r"""\documentclass[letterpaper,11pt]{article}
\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\input{glyphtounicode}

\pagestyle{fancy}
\fancyhf{}
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

\addtolength{\oddsidemargin}{-0.5in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1.0in}
\addtolength{\topmargin}{-.5in}
\addtolength{\textheight}{1.0in}

\urlstyle{same}

\raggedbottom
\raggedright

\titleformat{\section}{
  \vspace{-4pt}\scshape\raggedright\large
}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

\pdfgentounicode=1

\newcommand{\resumeItem}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      #1 & #2 \\
    \end{tabular*}\vspace{-7pt}
}

\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

\begin{document}
""")

        # Heading
        latex.append(r"\begin{center}")
        latex.append(f"    \\textbf{{\\Huge \\scshape {name}}} \\\\ \\small")
        contact_info = []
        if email:
            contact_info.append(f"\\href{{mailto:{email}}}{{{email}}}")
        if phone:
            contact_info.append(phone)
        if linkedin:
            contact_info.append(f"\\href{{https://{linkedin}}}{{linkedin.com/in/{linkedin.split('/')[-1]}}}")
        if github:
            contact_info.append(f"\\href{{https://{github}}}{{github.com/{github.split('/')[-1]}}}")
        latex.append("    " + " $|$ \n    ".join(contact_info))
        latex.append(r"\end{center}")
        latex.append("")

        # Summary
        if resume.summary:
            latex.append(r"\section{Summary}")
            latex.append(self.escape(resume.summary))
            latex.append("")

        # Education
        if resume.education:
            latex.append(r"\section{Education}")
            latex.append(r"  \resumeSubHeadingListStart")
            for edu in resume.education:
                inst = self.escape(edu.institution)
                degree = self.escape(edu.degree)
                dates = f"{edu.start_date} -- {edu.end_date}" if edu.end_date else edu.start_date
                latex.append("    \\resumeSubheading")
                latex.append(f"      {{{inst}}}{{}}")
                latex.append(f"      {{{degree}}}{{{self.escape(dates)}}}")
            latex.append(r"  \resumeSubHeadingListEnd")
            latex.append("")

        # Experience
        if resume.experience:
            latex.append(r"\section{Experience}")
            latex.append(r"  \resumeSubHeadingListStart")
            for exp in resume.experience:
                company = self.escape(exp.company)
                role = self.escape(exp.role)
                loc = self.escape(exp.location or "")
                dates = f"{exp.start_date} -- {exp.end_date}" if exp.end_date else exp.start_date
                latex.append("    \\resumeSubheading")
                latex.append(f"      {{{company}}}{{{loc}}}")
                latex.append(f"      {{{role}}}{{{self.escape(dates)}}}")
                if exp.bullets:
                    latex.append(r"      \resumeItemListStart")
                    for bullet in exp.bullets:
                        txt = self.escape(bullet.text)
                        latex.append(f"        \\resumeItem{{{txt}}}")
                    latex.append(r"      \resumeItemListEnd")
            latex.append(r"  \resumeSubHeadingListEnd")
            latex.append("")

        # Projects
        if resume.projects:
            latex.append(r"\section{Projects}")
            latex.append(r"  \resumeSubHeadingListStart")
            for proj in resume.projects:
                title = self.escape(proj.title)
                techs = ", ".join(self.escape(t) for t in proj.technologies)
                heading = f"\\textbf{{ {title} }}"
                if techs:
                    heading += f" $|$ \\emph{{ {techs} }}"
                latex.append("    \\resumeProjectHeading")
                latex.append(f"      {{{heading}}}{{}}")
                if proj.bullets:
                    latex.append(r"      \resumeItemListStart")
                    for proj_bullet in proj.bullets:
                        txt = self.escape(proj_bullet)
                        latex.append(f"        \\resumeItem{{{txt}}}")
                    latex.append(r"      \resumeItemListEnd")
            latex.append(r"  \resumeSubHeadingListEnd")
            latex.append("")

        # Technical Skills
        if resume.skills:
            latex.append(r"\section{Technical Skills}")
            latex.append(r" \begin{itemize}[leftmargin=0.15in, label={}]")
            latex.append(r"    \small{\item{")
            
            grouped_skills: dict[str, list[str]] = {}
            for sk in resume.skills:
                cat = sk.category or "Other"
                if cat not in grouped_skills:
                    grouped_skills[cat] = []
                grouped_skills[cat].append(sk.name)
                
            for cat, skill_names in grouped_skills.items():
                cat_escaped = self.escape(cat)
                skills_escaped = ", ".join(self.escape(s) for s in skill_names)
                latex.append(f"     \\textbf{{{cat_escaped}}}{{: {skills_escaped}}} \\\\")
                
            latex.append(r"    }}")
            latex.append(r" \end{itemize}")
            latex.append("")

        latex.append(r"\end{document}")
        return "\n".join(latex)
