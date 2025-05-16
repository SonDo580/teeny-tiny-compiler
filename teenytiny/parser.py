"""Teeny Tiny Grammar:

program ::= {statement}
statement ::= "PRINT" (expression | string) newline
    | "IF" comparison "THEN" newline {statement} "ENDIF" newline
    | "WHILE" comparison "REPEAT" newline {statement} "ENDWHILE" newline
    | "LABEL" identifier newline
    | "GOTO" identifier newline
    | "LET" identifier "=" expression newline
    | "INPUT" identifier newline
comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
expression ::= term {( "-" | "+" ) term}
term ::= unary {( "/" | "*" ) unary}
unary ::= ["+" | "-"] primary
primary ::= number | identifier
newline ::= '\n'+

*** Note ***

{} means zero or more
[] means zero or one,
+ means one or more,
() is for grouping,
| is a logical or
"""

import sys

from teenytiny_token import TokenType, Token
from lexer import Lexer


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer

        self.symbols = set()  # variables declared so far
        self.labels_declared = set()  # labels declared so far
        self.labels_goto = set()  # labels goto'ed so far

        # Initialize current_token and peek token
        self.current_token: Token = None
        self.peek_token: Token = None
        self.next_token()
        self.next_token()

    # Return true if the current token matches
    def check_token(self, token_type: TokenType):
        return token_type == self.current_token.type

    # Return true if the current token matches
    def check_peek(self, token_type: TokenType):
        return token_type == self.peek_token.type

    # Try to match and advance current token
    def match(self, token_type: TokenType):
        if not self.check_token(token_type):
            self.abort(
                f"Expected {token_type.name}, got {self.current_token.type.name}"
            )
        self.next_token()

    # Advance current token
    def next_token(self):
        self.current_token = self.peek_token
        self.peek_token = self.lexer.get_token()

    def abort(self, message: str):
        sys.exit(f"Error: {message}")

    # ===== Production rules =====

    # program ::= {statement}
    def program(self):
        print("PROGRAM")

        # Skip newlines at the beginning
        while self.check_token(TokenType.NEWLINE):
            self.next_token()

        # Parse all the statements
        while not self.check_token(TokenType.EOF):
            self.statement()

        # Check that all labels referenced in GOTO are declared
        for label in self.labels_goto:
            if label not in self.labels_declared:
                self.abort(f"GOTO undeclared label: {label}")

    def statement(self):
        # "PRINT" (expression | string) newline
        if self.check_token(TokenType.PRINT):
            print("STATEMENT-PRINT")
            self.next_token()
            if self.check_token(TokenType.STRING):
                self.next_token()
            else:
                self.expression()

        # "IF" comparison "THEN" newline {statement} "ENDIF" newline
        elif self.check_token(TokenType.IF):
            print("STATEMENT-IF")
            self.next_token()
            self.comparison()
            self.match(TokenType.THEN)
            self.newline()
            while not self.check_token(TokenType.ENDIF):
                self.statement()
            self.match(TokenType.ENDIF)

        # "WHILE" comparison "REPEAT" newline {statement newline} "ENDWHILE" newline
        elif self.check_token(TokenType.WHILE):
            print("STATEMENT-WHILE")
            self.next_token()
            self.comparison()
            self.match(TokenType.REPEAT)
            self.newline()
            while not self.check_token(TokenType.ENDWHILE):
                self.statement()
            self.match(TokenType.ENDWHILE)

        # "LABEL" identifier newline
        elif self.check_token(TokenType.LABEL):
            print("STATEMENT-LABEL")
            self.next_token()

            # make sure the label doesn't already exist
            if self.current_token.text in self.labels_declared:
                self.abort(f"Label already exists: {self.current_token.text}")

            self.match(TokenType.IDENTIFIER)

        # "GOTO" identifier newline
        elif self.check_token(TokenType.GOTO):
            print("STATEMENT-GOTO")
            self.next_token()
            self.labels_goto.add(self.current_token.text)
            self.match(TokenType.IDENTIFIER)

        # "LET" identifier "=" expression newline
        elif self.check_token(TokenType.LET):
            print("STATEMENT-LET")
            self.next_token()

            # Declare the variable if not exist in symbols table
            if self.current_token.text not in self.symbols:
                self.symbols.add(self.current_token.text)

            self.match(TokenType.IDENTIFIER)
            self.match(TokenType.EQ)

            self.expression()

        # "INPUT" identifier newline
        elif self.check_token(TokenType.INPUT):
            print("STATEMENT-INPUT")
            self.next_token()

            # Declare the variable if not exist in symbols table
            if self.current_token.text not in self.symbols:
                self.symbols.add(self.current_token.text)

            self.match(TokenType.IDENTIFIER)

        else:
            self.abort(
                f"Invalid statement at {self.current_token.text} ({self.current_token.type.name})"
            )

        self.newline()

    def newline(self):
        print("NEWLINE")

        # Require at least 1 newline. Allow extra newlines
        self.match(TokenType.NEWLINE)
        while self.check_token(TokenType.NEWLINE):
            self.next_token()

    # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
    def comparison(self):
        print("COMPARISON")
        self.expression()
        if self.is_comparison_operator():
            self.next_token()
            self.expression()
        else:
            self.abort(f"Expected comparison operator at {self.current_token.text}")
        while self.is_comparison_operator():
            self.next_token()
            self.expression()

    def is_comparison_operator(self):
        return (
            self.check_token(TokenType.GT)
            or self.check_token(TokenType.GTEQ)
            or self.check_token(TokenType.LT)
            or self.check_token(TokenType.LTEQ)
            or self.check_token(TokenType.EQEQ)
            or self.check_token(TokenType.NOTEQ)
        )

    # expression ::= term {( "-" | "+" ) term}
    def expression(self):
        print("EXPRESSION")
        self.term()
        while self.check_token(TokenType.PLUS) or self.check_token(TokenType.MINUS):
            self.next_token()
            self.term()

    # term ::= unary {( "/" | "*" ) unary}
    def term(self):
        print("TERM")
        self.unary()
        while self.check_token(TokenType.ASTERISK) or self.check_token(TokenType.SLASH):
            self.next_token()
            self.unary()

    # unary ::= ["+" | "-"] primary
    def unary(self):
        print("UNARY")
        if self.check_token(TokenType.PLUS) or self.check_token(TokenType.MINUS):
            self.next_token()
        self.primary()

    # primary ::= number | identifier
    def primary(self):
        print(f"PRIMARY ({self.current_token.text})")
        if self.check_token(TokenType.NUMBER):
            self.next_token()
        elif self.check_token(TokenType.IDENTIFIER):
            # Ensure the variable already declared
            if self.current_token.text not in self.symbols:
                self.abort(
                    f"Referencing variable before assignment: {self.current_token.text}"
                )
            self.next_token()
        else:
            self.abort(f"Unexpected token at {self.current_token.text}")
