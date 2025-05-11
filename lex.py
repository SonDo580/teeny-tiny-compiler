import sys

from teenytiny_token import Token, TokenType


class Lexer:
    def __init__(self, source: str):
        # append a newline to simplify lexing/parsing the last token
        self.source = source + "\n"

        self.current_char = ""
        self.current_pos = -1
        self.next_char()

    # Process the next character
    def next_char(self) -> None:
        self.current_pos += 1
        if self.current_pos >= len(self.source):
            self.current_char = "\0"
        else:
            self.current_char = self.source[self.current_pos]

    # Return the lookahead character
    def peek(self) -> str:
        if self.current_pos + 1 >= len(self.source):
            return "\0"
        return self.source[self.current_pos + 1]

    # Invalid token found -> print error and exit
    def abort(self, message: str) -> None:
        sys.exit(f"Lexing error. {message}")

    # Skip whitespaces except newline (use to indicate end of statement)
    def skip_whitespaces(self):
        while self.current_char in [" ", "\t", "\r"]:
            self.next_char()

    # Skip a comment in code
    def skip_comment(self):
        if self.current_char == "#":
            while self.current_char != "\n":
                self.next_char()

    # Return the next token:
    def get_token(self) -> Token:
        self.skip_whitespaces()
        self.skip_comment()
        token = None

        if self.current_char == "+":
            token = Token(self.current_char, TokenType.PLUS)
        elif self.current_char == "-":
            token = Token(self.current_char, TokenType.MINUS)
        elif self.current_char == "*":
            token = Token(self.current_char, TokenType.ASTERISK)
        elif self.current_char == "/":
            token = Token(self.current_char, TokenType.SLASH)
        elif self.current_char == "\n":
            token = Token(self.current_char, TokenType.NEWLINE)
        elif self.current_char == "\0":
            token = Token("", TokenType.EOF)
        elif self.current_char == "=":
            # Check if this token is '=' or '=='
            if self.peek() == "=":
                last_char = self.current_char
                self.next_char()
                token = Token(last_char + self.current_char, TokenType.EQEQ)
            else:
                token = Token(self.current_char, TokenType.EQ)
        elif self.current_char == ">":
            # Check if this token is '>' or '>='
            if self.peek() == "=":
                last_char = self.current_char
                self.next_char()
                token = Token(last_char + self.current_char, TokenType.GTEQ)
            else:
                token = Token(self.current_char, TokenType.GT)
        elif self.current_char == "<":
            # Check if this token is '<' or '<='
            if self.peek() == "=":
                last_char = self.current_char
                self.next_char()
                token = Token(last_char + self.current_char, TokenType.LTEQ)
            else:
                token = Token(self.current_char, TokenType.LT)
        elif self.current_char == "!":
            if self.peek() == "=":
                last_char = self.current_char
                self.next_char()
                token = Token(last_char + self.current_char, TokenType.NOTEQ)
            else:
                self.abort(f"Expected !=, got !{self.peek()}")
        elif self.current_char == '"':
            # Handle string: get characters between quotations
            self.next_char()
            start_pos = self.current_pos

            while self.current_char != '"':
                # Forbid special characters to simplify implementation
                if self.current_char in ["\r", "\n", "\t", "\\", "%"]:
                    self.abort("Illegal characters in string.")
                self.next_char()

            token_text = self.source[start_pos : self.current_pos]
            token = Token(token_text, TokenType.STRING)
        elif self.current_char.isdigit():
            # Handle number: Get all consecutive digits
            start_pos = self.current_pos
            while self.peek().isdigit():
                self.next_char()

            # Handle decimal part
            if self.peek() == ".":
                self.next_char()

                # Must have at least 1 digit after decimal point
                if not self.peek().isdigit():
                    self.abort("Illegal character in number.")
                while self.peek().isdigit():
                    self.next_char()

            token_text = self.source[start_pos : self.current_pos + 1]
            token = Token(token_text, TokenType.NUMBER)
        elif self.current_char.isalpha():
            # Handle keyword/identifier
            start_pos = self.current_pos
            while self.peek().isalnum():
                self.next_char()

            token_text = self.source[start_pos : self.current_pos + 1]
            keyword_type = Token.get_keyword_type(token_text)
            if keyword_type is None:
                token = Token(token_text, TokenType.IDENTIFIER)
            else:
                token = Token(token_text, keyword_type)
        else:
            self.abort(f"Unknown token: {self.current_char}")

        self.next_char()
        return token
