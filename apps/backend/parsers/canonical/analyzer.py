import re
from typing import List, Optional, Tuple
from parsers.ast.nodes import (
    ASTNode, DocumentNode, TextNode, CommandNode, GroupNode, EnvironmentNode
)
from domain.resume.models import (
    Resume, Experience, ExperienceBullet, Project, Skill, Education, Certification, Achievement, SkillCategory
)


def node_to_text(node: ASTNode) -> str:
    if isinstance(node, TextNode):
        return node.value
    elif isinstance(node, GroupNode):
        return "".join(node_to_text(c) for c in node.children)
    elif isinstance(node, EnvironmentNode):
        return "".join(node_to_text(c) for c in node.children)
    elif isinstance(node, CommandNode):
        if node.name == "href" and len(node.arguments) >= 2:
            return node_to_text(node.arguments[1])
        return "".join(node_to_text(arg) for arg in node.arguments)
    return ""


class LaTeXSemanticAnalyzer:
    def __init__(self):
        self.resume = Resume()

    def analyze(self, doc: DocumentNode) -> Resume:
        current_section_name: Optional[str] = None
        current_section_nodes: list[ASTNode] = []
        
        pre_section_nodes: list[ASTNode] = []
        first_section_found = False

        for node in doc.children:
            if isinstance(node, CommandNode) and node.name == "section":
                if current_section_name:
                    self._parse_section(current_section_name, current_section_nodes)
                current_section_name = node_to_text(node).strip()
                current_section_nodes = []
                first_section_found = True
            else:
                if not first_section_found:
                    pre_section_nodes.append(node)
                else:
                    current_section_nodes.append(node)
                    
        if current_section_name:
            self._parse_section(current_section_name, current_section_nodes)

        self._parse_contact_info(pre_section_nodes)
        
        return self.resume

    def _parse_contact_info(self, nodes: List[ASTNode]):
        text = "".join(node_to_text(n) for n in nodes)
        
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match:
            self.resume.metadata.additional_metadata["email"] = email_match.group(0)

        phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        if phone_match:
            self.resume.metadata.additional_metadata["phone"] = phone_match.group(0)
            
        github_match = re.search(r'github\.com/[\w\.-]+', text, re.IGNORECASE)
        if github_match:
            self.resume.metadata.additional_metadata["github"] = github_match.group(0)
            
        linkedin_match = re.search(r'linkedin\.com/in/[\w\.-]+', text, re.IGNORECASE)
        if linkedin_match:
            self.resume.metadata.additional_metadata["linkedin"] = linkedin_match.group(0)

        def find_name_in_nodes(node_list: List[ASTNode]) -> Optional[str]:
            for node in node_list:
                children = []
                if isinstance(node, GroupNode):
                    children = node.children
                elif isinstance(node, CommandNode):
                    for arg in node.arguments:
                        children.extend(arg.children)
                
                for child in children:
                    if isinstance(child, CommandNode) and child.name in ("Huge", "huge", "LARGE", "Large"):
                        return node_to_text(node).strip()
                
                res = find_name_in_nodes(children)
                if res:
                    return res
            return None

        name = find_name_in_nodes(nodes)
        if name:
            self.resume.metadata.additional_metadata["name"] = name

    def _parse_section(self, name: str, nodes: List[ASTNode]):
        name_lower = name.lower()
        if "education" in name_lower:
            self._parse_education(nodes)
        elif "experience" in name_lower or "employment" in name_lower or "work" in name_lower:
            self._parse_experience(nodes)
        elif "project" in name_lower:
            self._parse_projects(nodes)
        elif "skills" in name_lower or "technical" in name_lower:
            self._parse_skills(nodes)
        elif "certif" in name_lower:
            self._parse_certifications(nodes)
        elif "achieve" in name_lower or "award" in name_lower:
            self._parse_achievements(nodes)

    def _parse_education(self, nodes: List[ASTNode]):
        flat_commands = []
        
        def collect_commands(node_list: List[ASTNode]):
            for node in node_list:
                if isinstance(node, CommandNode):
                    flat_commands.append(node)
                    for arg in node.arguments:
                        collect_commands(arg.children)
                elif isinstance(node, GroupNode):
                    collect_commands(node.children)

        collect_commands(nodes)
        
        for cmd in flat_commands:
            if cmd.name == "resumeSubheading":
                args = [node_to_text(arg).strip() for arg in cmd.arguments]
                if len(args) >= 4:
                    inst, _loc, degree, dates = args[0], args[1], args[2], args[3]
                    start, end = self._parse_dates(dates)
                    self.resume.education.append(Education(
                        institution=inst,
                        degree=degree,
                        field=None,
                        cgpa=None,
                        start_date=start,
                        end_date=end
                    ))

    def _parse_experience(self, nodes: List[ASTNode]):
        flat_commands = []
        
        def collect_commands(node_list: List[ASTNode]):
            for node in node_list:
                if isinstance(node, CommandNode):
                    flat_commands.append(node)
                    for arg in node.arguments:
                        collect_commands(arg.children)
                elif isinstance(node, GroupNode):
                    collect_commands(node.children)

        collect_commands(nodes)
        
        current_exp = None
        for cmd in flat_commands:
            if cmd.name == "resumeSubheading":
                args = [node_to_text(arg).strip() for arg in cmd.arguments]
                if len(args) >= 4:
                    company, loc, role, dates = args[0], args[1], args[2], args[3]
                    start, end = self._parse_dates(dates)
                    current_exp = Experience(
                        company=company,
                        role=role,
                        location=loc,
                        start_date=start,
                        end_date=end,
                        bullets=[]
                    )
                    self.resume.experience.append(current_exp)
            elif cmd.name in ("resumeItem", "item"):
                if current_exp:
                    txt = node_to_text(cmd).strip()
                    if txt:
                        current_exp.bullets.append(ExperienceBullet(text=txt))

    def _parse_projects(self, nodes: List[ASTNode]):
        flat_commands = []
        
        def collect_commands(node_list: List[ASTNode]):
            for node in node_list:
                if isinstance(node, CommandNode):
                    flat_commands.append(node)
                    for arg in node.arguments:
                        collect_commands(arg.children)
                elif isinstance(node, GroupNode):
                    collect_commands(node.children)

        collect_commands(nodes)
        
        current_proj = None
        for cmd in flat_commands:
            if cmd.name == "resumeProjectHeading":
                args = [node_to_text(arg).strip() for arg in cmd.arguments]
                if len(args) >= 2:
                    title_tech, _date = args[0], args[1]
                    parts = re.split(r'\||\$\|\$', title_tech)
                    title = parts[0].strip()
                    title = re.sub(r'\\textbf\{|\}', '', title).strip()
                    
                    techs = []
                    if len(parts) > 1:
                        tech_str = parts[1].strip()
                        tech_str = re.sub(r'\\emph\{|\}', '', tech_str).strip()
                        techs = [t.strip() for t in tech_str.split(',') if t.strip()]
                        
                    current_proj = Project(
                        title=title,
                        description=None,
                        technologies=techs,
                        bullets=[]
                    )
                    self.resume.projects.append(current_proj)
            elif cmd.name in ("resumeItem", "item"):
                if current_proj:
                    txt = node_to_text(cmd).strip()
                    if txt:
                        current_proj.bullets.append(txt)

    def _parse_skills(self, nodes: List[ASTNode]):
        for node in nodes:
            text_lines = node_to_text(node).split('\n')
            for line in text_lines:
                if ":" in line:
                    parts = line.split(":", 1)
                    cat_name = parts[0].strip()
                    skills_str = parts[1].strip()
                    cat_name = re.sub(r'\\[a-zA-Z]+|\{|\}', '', cat_name).strip()
                    
                    skill_cat = self._map_skill_category(cat_name)
                    
                    skills = [s.strip() for s in skills_str.split(',') if s.strip()]
                    for sk in skills:
                        sk_clean = re.sub(r'\}|\{', '', sk).strip()
                        if sk_clean:
                            self.resume.skills.append(Skill(
                                name=sk_clean,
                                category=skill_cat or cat_name
                            ))

    def _map_skill_category(self, cat_name: str) -> Optional[SkillCategory]:
        cat_lower = cat_name.lower()
        if "lang" in cat_lower:
            return SkillCategory.PROGRAMMING_LANGUAGE
        elif "framework" in cat_lower:
            return SkillCategory.FRAMEWORK
        elif "tool" in cat_lower:
            return SkillCategory.TOOL
        elif "cloud" in cat_lower:
            return SkillCategory.CLOUD
        elif "db" in cat_lower or "database" in cat_lower:
            return SkillCategory.DATABASE
        elif "devops" in cat_lower:
            return SkillCategory.DEVOPS
        elif "frontend" in cat_lower or "web" in cat_lower:
            return SkillCategory.FRONTEND
        elif "backend" in cat_lower:
            return SkillCategory.BACKEND
        elif "ai" in cat_lower or "machine learning" in cat_lower or "ml" in cat_lower:
            return SkillCategory.AI
        return None

    def _parse_certifications(self, nodes: List[ASTNode]):
        text = "".join(node_to_text(n) for n in nodes)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        for line in lines:
            parts = line.split("-", 1)
            name = parts[0].strip()
            issuer = parts[1].strip() if len(parts) > 1 else "Unknown"
            self.resume.certifications.append(Certification(
                name=name,
                issuer=issuer
            ))

    def _parse_achievements(self, nodes: List[ASTNode]):
        text = "".join(node_to_text(n) for n in nodes)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        for line in lines:
            self.resume.achievements.append(Achievement(
                title=line,
                description=None
            ))

    def _parse_dates(self, date_str: str) -> Tuple[str, Optional[str]]:
        parts = re.split(r'--|-', date_str)
        if len(parts) >= 2:
            return parts[0].strip(), parts[1].strip()
        return date_str.strip(), None
