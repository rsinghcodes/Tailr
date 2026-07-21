from typing import List
from parsers.tokenizer.token_types import Token, TokenType


class LaTeXLexer:
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.length = len(source)

    def peek(self, offset: int = 0) -> str:
        if self.position + offset >= self.length:
            return ""
        return self.source[self.position + offset]

    def advance(self) -> str:
        if self.position >= self.length:
            return ""
        char = self.source[self.position]
        self.position += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def tokenize(self) -> List[Token]:
        tokens = []
        while self.position < self.length:
            char = self.peek()
            
            # Record start line/col
            start_line = self.line
            start_col = self.column

            if char == '\r':
                self.advance()
                if self.peek() == '\n':
                    self.advance()
                tokens.append(Token(type=TokenType.NEWLINE, value="\n", line=start_line, column=start_col))
                continue
            elif char == '\n':
                self.advance()
                tokens.append(Token(type=TokenType.NEWLINE, value="\n", line=start_line, column=start_col))
                continue
            elif char.isspace():
                val = ""
                while self.peek().isspace() and self.peek() not in ('\r', '\n'):
                    val += self.advance()
                tokens.append(Token(type=TokenType.WHITESPACE, value=val, line=start_line, column=start_col))
                continue
            elif char == '%':
                val = ""
                while self.peek() not in ('\r', '\n', ""):
                    val += self.advance()
                tokens.append(Token(type=TokenType.COMMENT, value=val, line=start_line, column=start_col))
                continue
            elif char == '\\':
                val = self.advance()  # Keep '\'
                next_char = self.peek()
                if next_char.isalpha():
                    while self.peek().isalpha():
                        val += self.advance()
                    tokens.append(Token(type=TokenType.COMMAND, value=val, line=start_line, column=start_col))
                elif next_char in ('*', '&', '%', '$', '#', '_', '{', '}', '~', '^', '\\'):
                    val += self.advance()
                    tokens.append(Token(type=TokenType.COMMAND, value=val, line=start_line, column=start_col))
                else:
                    tokens.append(Token(type=TokenType.TEXT, value=val, line=start_line, column=start_col))
                continue
            elif char == '{':
                self.advance()
                tokens.append(Token(type=TokenType.LBRACE, value="{", line=start_line, column=start_col))
                continue
            elif char == '}':
                self.advance()
                tokens.append(Token(type=TokenType.RBRACE, value="}", line=start_line, column=start_col))
                continue
            elif char == '[':
                self.advance()
                tokens.append(Token(type=TokenType.LBRACKET, value="[", line=start_line, column=start_col))
                continue
            elif char == ']':
                self.advance()
                tokens.append(Token(type=TokenType.RBRACKET, value="]", line=start_line, column=start_col))
                continue
            else:
                val = ""
                while self.position < self.length:
                    c = self.peek()
                    if c in ('\\', '%', '{', '}', '[', ']', '\n', '\r') or c.isspace():
                        break
                    val += self.advance()
                tokens.append(Token(type=TokenType.TEXT, value=val, line=start_line, column=start_col))
                
        tokens.append(Token(type=TokenType.EOF, value="", line=self.line, column=self.column))
        return tokens
