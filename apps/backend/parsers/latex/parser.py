from typing import List, Optional
from parsers.tokenizer.token_types import Token, TokenType
from parsers.ast.nodes import (
    ASTNode, DocumentNode, TextNode, CommandNode, GroupNode
)


class LaTeXParser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def peek(self, offset: int = 0) -> Token:
        idx = self.current + offset
        if idx >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[idx]

    def advance(self) -> Token:
        t = self.peek()
        if t.type != TokenType.EOF:
            self.current += 1
        return t

    def is_eof(self) -> bool:
        return self.peek().type == TokenType.EOF

    def consume(self, expected_type: TokenType, error_msg: str) -> Token:
        t = self.peek()
        if t.type == expected_type:
            return self.advance()
        raise ValueError(
            f"Parser Error at line {t.line}, col {t.column}: {error_msg}. Got: {t.value} ({t.type})"
        )

    def parse(self) -> DocumentNode:
        doc = DocumentNode(
            line=1,
            column=1,
            children=self.parse_sequence(until_types=[TokenType.EOF])
        )
        return doc

    def parse_sequence(self, until_types: List[TokenType]) -> List[ASTNode]:
        nodes = []
        while not self.is_eof():
            t = self.peek()
            if t.type in until_types:
                break
            
            node = self.parse_expression()
            if node:
                nodes.append(node)
        return nodes

    def parse_expression(self) -> Optional[ASTNode]:
        t = self.peek()
        
        if t.type == TokenType.COMMAND:
            return self.parse_command()
                
        elif t.type == TokenType.LBRACE:
            return self.parse_group(is_bracket=False)
            
        elif t.type == TokenType.LBRACKET:
            return self.parse_group(is_bracket=True)
            
        elif t.type in (TokenType.TEXT, TokenType.WHITESPACE, TokenType.NEWLINE):
            self.advance()
            return TextNode(line=t.line, column=t.column, value=t.value)
            
        elif t.type == TokenType.COMMENT:
            self.advance()
            return TextNode(line=t.line, column=t.column, value=t.value + "\n")
            
        else:
            self.advance()
            return None

    def parse_command(self) -> CommandNode:
        t = self.advance()  # Consume command
        cmd_name = t.value[1:]  # strip leading \
        cmd_node = CommandNode(line=t.line, column=t.column, name=cmd_name)
        
        while True:
            # Skip any whitespace/newline/comment tokens before peeking at the argument brace
            idx = 0
            while self.peek(idx).type in (TokenType.WHITESPACE, TokenType.NEWLINE, TokenType.COMMENT):
                idx += 1
                
            nxt = self.peek(idx)
            if nxt.type in (TokenType.LBRACE, TokenType.LBRACKET):
                # Consume the skipped spacing tokens
                for _ in range(idx):
                    self.advance()
                is_bracket = nxt.type == TokenType.LBRACKET
                cmd_node.arguments.append(self.parse_group(is_bracket=is_bracket))
            else:
                break
                
        return cmd_node

    def parse_group(self, is_bracket: bool) -> GroupNode:
        start_tok = self.advance()
        close_type = TokenType.RBRACE if not is_bracket else TokenType.RBRACKET
        
        group_node = GroupNode(
            line=start_tok.line,
            column=start_tok.column,
            is_bracket=is_bracket,
            children=self.parse_sequence(until_types=[close_type])
        )
        
        self.consume(close_type, f"Missing matching closing {'}' if not is_bracket else ']'}")
        return group_node
