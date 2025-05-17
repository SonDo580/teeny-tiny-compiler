import sys


class Emitter:
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.header = ""
        self.code = ""

    def emit(self, code: str):
        self.code += code

    def emit_line(self, code: str):
        self.code += code + "\n"

    def header_line(self, code: str):
        self.header += code + "\n"

    def write_file(self):
        file_path = self.output_path
        try:
            with open(file_path, "w") as output_file:
                output_file.write(self.header + self.code)
        except FileNotFoundError:
            sys.exit(f"File '{file_path}' not found")
        except IOError as e:
            sys.exit(f"Error writing to file {file_path}: {e}")
