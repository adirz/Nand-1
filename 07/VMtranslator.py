#!/usr/bin/python
import Parser
from CodeWriter import CodeWriter
import sys, os

class VMtranslator(object):
    def __init__(self, input_file_path):
        self.input_file_path = input_file_path
        self.code_writer = CodeWriter(input_file_path.replace(".vm", ".asm"))

    def translate(self):
        self.parser = Parser.Parser(self.input_file_path)
        while self.parser.has_more_commands():
            self.parser.advance()
            self._gen_command()
        self.code_writer.close()

    def _gen_command(self):
        command_type = self.parser.command_type()
        if command_type == Parser.C_PUSH or command_type == Parser.C_POP:
            self.code_writer.write_push_pop(self.parser.current_commands[0], self.parser.arg1(), self.parser.arg2())
        elif command_type == Parser.C_ARITHMETIC:
            self.code_writer.write_arithmetic(self.parser.arg1())

def main():
    if not len(sys.argv) == 2:
        print("Usage: assembler.py <input.asm>")
        return
    in_path = sys.argv[1]
    if not os.path.isdir(in_path):
        file_name = os.path.splitext(in_path)[0]
        VMtranslator(in_path).translate()
        return
    for file_name in os.listdir(in_path):
        if file_name.endswith(".vm"):
            VMtranslator(os.path.join(in_path, file_name)).translate()

if "__main__" == __name__:
    main()
