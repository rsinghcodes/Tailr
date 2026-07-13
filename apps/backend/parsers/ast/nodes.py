from typing import List, Any
from pydantic import BaseModel, Field


class ASTNode(BaseModel):
    line: int
    column: int

    def accept(self, visitor: "ASTVisitor") -> Any:
        raise NotImplementedError()


class TextNode(ASTNode):
    value: str

    def accept(self, visitor: "ASTVisitor") -> Any:
        return visitor.visit_text(self)


class CommandNode(ASTNode):
    name: str  # e.g., "section", "resumeSubheading"
    arguments: List["GroupNode"] = Field(default_factory=list)  # List of {arg} or [arg] groups

    def accept(self, visitor: "ASTVisitor") -> Any:
        return visitor.visit_command(self)


class GroupNode(ASTNode):
    # e.g. { ... } or [ ... ]
    is_bracket: bool = False  # True for [ ... ], False for { ... }
    children: List[ASTNode] = Field(default_factory=list)

    def accept(self, visitor: "ASTVisitor") -> Any:
        return visitor.visit_group(self)


class EnvironmentNode(ASTNode):
    # e.g. \begin{env} ... \end{env}
    name: str  # e.g., "document", "itemize"
    arguments: List[GroupNode] = Field(default_factory=list)
    children: List[ASTNode] = Field(default_factory=list)

    def accept(self, visitor: "ASTVisitor") -> Any:
        return visitor.visit_environment(self)


class DocumentNode(ASTNode):
    # Root node of the parsed document
    children: List[ASTNode] = Field(default_factory=list)

    def accept(self, visitor: "ASTVisitor") -> Any:
        return visitor.visit_document(self)


class ASTVisitor:
    def visit_document(self, node: DocumentNode) -> Any:
        pass

    def visit_text(self, node: TextNode) -> Any:
        pass

    def visit_command(self, node: CommandNode) -> Any:
        pass

    def visit_group(self, node: GroupNode) -> Any:
        pass

    def visit_environment(self, node: EnvironmentNode) -> Any:
        pass
