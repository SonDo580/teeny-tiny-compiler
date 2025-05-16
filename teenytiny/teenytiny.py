import sys
from lexer import Lexer
from parser import Parser


def main():
    print("Teeny Tiny Compiler")

    if len(sys.argv) != 2:
        sys.exit("Usage: python teenytiny.py <source_file>")

    file_path = sys.argv[1]
    try:
        with open(file_path, 'r') as inputFile:
            source = inputFile.read()
    except FileNotFoundError:
        sys.exit(f"File '{file_path}' not found")
    except IOError as e:
        sys.exit(f"Error reading file {file_path}: {e}")

    lexer = Lexer(source)
    parser = Parser(lexer)

    parser.program()
    print("Parsing complete")
    
if __name__ == "__main__":
    main()
