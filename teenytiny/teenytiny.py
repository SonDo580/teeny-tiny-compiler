from lexer import Lexer
from teenytiny_token import TokenType


def main():
    source = "IF+-123 foo*THEN/"
    lexer = Lexer(source)

    token = lexer.get_token()
    while token.type != TokenType.EOF:
        print(token.type)
        token = lexer.get_token()


if __name__ == "__main__":
    main()
