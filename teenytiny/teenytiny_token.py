from enum import Enum, auto

class TokenType(Enum):
	EOF = auto()
	NEWLINE = auto()
	NUMBER = auto()
	IDENTIFIER = auto()
	STRING = auto()
	
	# Keywords.
	LABEL = auto()
	GOTO = auto()
	PRINT = auto()
	INPUT = auto()
	LET = auto()
	IF = auto()
	THEN = auto()
	ENDIF = auto()
	WHILE = auto()
	REPEAT = auto()
	ENDWHILE = auto()
	
	# Operators.
	PLUS = auto()
	MINUS = auto() 
	ASTERISK = auto()
	SLASH = auto()
	EQ = auto()
	EQEQ = auto()
	NOTEQ = auto()
	LT = auto()
	LTEQ = auto()
	GT = auto()
	GTEQ = auto()


class Token:
	def __init__(self, token_text: str, token_type: TokenType):
		self.text = token_text  # used for number/string/identifier
		self.type = token_type

	@staticmethod
	def get_keyword_type(token_text: str) -> TokenType | None:
		for type in TokenType:
			if type.name == token_text:
				return type
		return None