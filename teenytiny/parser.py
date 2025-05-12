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


class Parser:
    def __init__(self, lexer):
        pass
