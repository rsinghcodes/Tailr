from enum import Enum
from pydantic import BaseModel


class TokenType(str, Enum):
    COMMAND = "COMMAND"              # e.g., \resumeSubheading, \section, \textbf
    TEXT = "TEXT"                    # e.g., "John Doe", "Experience"
    LBRACE = "LBRACE"                # {
    RBRACE = "RBRACE"                # }
    LBRACKET = "LBRACKET"            # [
    RBRACKET = "RBRACKET"            # ]
    COMMENT = "COMMENT"              # e.g., % Comments
    NEWLINE = "NEWLINE"              # \n
    WHITESPACE = "WHITESPACE"        # space, tab
    EOF = "EOF"                      # End of File


class Token(BaseModel):
    type: TokenType
    value: str
    line: int
    column: int
