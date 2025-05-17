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
from emitter import Emitter


class Parser:
    def __init__(self, lexer: Lexer, emitter: Emitter):
        self.lexer = lexer
        self.emitter = emitter

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
        self.emitter.header_line("#include <stdio.h>")
        self.emitter.header_line("int main(void) {")

        # Skip newlines at the beginning
        while self.check_token(TokenType.NEWLINE):
            self.next_token()

        # Parse all the statements
        while not self.check_token(TokenType.EOF):
            self.statement()

        self.emitter.emit_line("return 0;")
        self.emitter.emit_line("}")

        # Check that all labels referenced in GOTO are declared
        for label in self.labels_goto:
            if label not in self.labels_declared:
                self.abort(f"GOTO undeclared label: {label}")

    def statement(self):
        # "PRINT" (expression | string) newline
        if self.check_token(TokenType.PRINT):
            self.next_token()

            if self.check_token(TokenType.STRING):
                # Print a string
                self.emitter.emit_line(f'printf("{self.current_token.text}");')
                self.next_token()
            else:
                # Print the expression result as a float
                self.emitter.emit(f'printf("%.2f", (float)(')
                self.expression()
                self.emitter.emit_line("));")

        # "IF" comparison "THEN" newline {statement} "ENDIF" newline
        elif self.check_token(TokenType.IF):
            self.next_token()
            self.emitter.emit("if(")
            self.comparison()

            self.match(TokenType.THEN)
            self.newline()
            self.emitter.emit_line("){")

            while not self.check_token(TokenType.ENDIF):
                self.statement()

            self.match(TokenType.ENDIF)
            self.emitter.emit_line("}")

        # "WHILE" comparison "REPEAT" newline {statement newline} "ENDWHILE" newline
        elif self.check_token(TokenType.WHILE):
            self.next_token()
            self.emitter.emit("while(")
            self.comparison()

            self.match(TokenType.REPEAT)
            self.newline()
            self.emitter.emit_line("){")

            while not self.check_token(TokenType.ENDWHILE):
                self.statement()

            self.match(TokenType.ENDWHILE)
            self.emitter.emit_line("}")

        # "LABEL" identifier newline
        elif self.check_token(TokenType.LABEL):
            self.next_token()

            # make sure the label doesn't already exist
            if self.current_token.text in self.labels_declared:
                self.abort(f"Label already exists: {self.current_token.text}")

            self.emitter.emit_line(f"{self.current_token.text}:")
            self.match(TokenType.IDENTIFIER)

        # "GOTO" identifier newline
        elif self.check_token(TokenType.GOTO):
            self.next_token()
            self.labels_goto.add(self.current_token.text)

            self.emitter.emit_line(f"goto {self.current_token.text};")
            self.match(TokenType.IDENTIFIER)

        # "LET" identifier "=" expression newline
        elif self.check_token(TokenType.LET):
            self.next_token()

            # Declare the variable if not exist in symbols table
            if self.current_token.text not in self.symbols:
                self.symbols.add(self.current_token.text)
                self.emitter.header_line(f"float {self.current_token.text};")

            self.emitter.emit(f"{self.current_token.text} = ")
            self.match(TokenType.IDENTIFIER)
            self.match(TokenType.EQ)

            self.expression()
            self.emitter.emit_line(";")

        # "INPUT" identifier newline
        elif self.check_token(TokenType.INPUT):
            self.next_token()

            # Declare the variable if not exist in symbols table
            if self.current_token.text not in self.symbols:
                self.symbols.add(self.current_token.text)
                self.emitter.header_line(f"float {self.current_token.text};")

            # Emit scanf but and input validation code
            # If invalid, set the value to 0 and reset the input
            self.emitter.emit_line(
                f"if(" + f'scanf("%f", &{self.current_token.text})' + " == 0){"
            )
            self.emitter.emit_line(f"{self.current_token.text} = 0;")
            self.emitter.emit_line('scanf("%*s");')
            self.emitter.emit_line("}")
            self.match(TokenType.IDENTIFIER)

        else:
            self.abort(
                f"Invalid statement at {self.current_token.text} ({self.current_token.type.name})"
            )

        self.newline()

    def newline(self):
        # Require at least 1 newline. Allow extra newlines
        self.match(TokenType.NEWLINE)
        while self.check_token(TokenType.NEWLINE):
            self.next_token()

    # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
    def comparison(self):
        self.expression()

        if self.is_comparison_operator():
            self.emitter.emit(self.current_token.text)
            self.next_token()
            self.expression()
        else:
            self.abort(f"Expected comparison operator at {self.current_token.text}")

        while self.is_comparison_operator():
            self.emitter.emit(self.current_token.text)
            self.next_token()
            self.expression()

    def is_comparison_operator(self) -> bool:
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
        self.term()
        while self.check_token(TokenType.PLUS) or self.check_token(TokenType.MINUS):
            self.emitter.emit(self.current_token.text)
            self.next_token()
            self.term()

    # term ::= unary {( "/" | "*" ) unary}
    def term(self):
        self.unary()
        while self.check_token(TokenType.ASTERISK) or self.check_token(TokenType.SLASH):
            self.emitter.emit(self.current_token.text)
            self.next_token()
            self.unary()

    # unary ::= ["+" | "-"] primary
    def unary(self):
        if self.check_token(TokenType.PLUS) or self.check_token(TokenType.MINUS):
            self.emitter.emit(self.current_token.text)
            self.next_token()
        self.primary()

    # primary ::= number | identifier
    def primary(self):
        if self.check_token(TokenType.NUMBER):
            self.emitter.emit(self.current_token.text)
            self.next_token()
        elif self.check_token(TokenType.IDENTIFIER):
            # Ensure the variable already declared
            if self.current_token.text not in self.symbols:
                self.abort(
                    f"Referencing variable before assignment: {self.current_token.text}"
                )
            self.emitter.emit(self.current_token.text)
            self.next_token()
        else:
            self.abort(f"Unexpected token at {self.current_token.text}")
