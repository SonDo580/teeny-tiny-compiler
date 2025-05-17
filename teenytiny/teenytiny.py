import sys

from lexer import Lexer
from parser import Parser
from emitter import Emitter

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
    emitter = Emitter("out.c")
    parser = Parser(lexer, emitter)

    parser.program()
    emitter.write_file()
    print("Compiling completed.")
    
if __name__ == "__main__":
    main()
