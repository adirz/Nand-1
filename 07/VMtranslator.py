#!/usr/bin/python
import Parser
from CodeWriter import CodeWriter
import sys, os

class VMtranslator(object):
    def __init__(self, input_file_path):
        self.input_file_path = input_file_path
        if not os.path.isdir(input_file_path):
            self.code_writer = CodeWriter(input_file_path.replace(".vm", ".asm"))
        else:
            file_name = input_file_path.split("/")
            file_name = file_name[len(file_name)-1]
            file_name = file_name.split("\\")
            file_name = file_name[len(file_name)-1]
            path = os.path.join(input_file_path, file_name + ".asm")
            self.code_writer = CodeWriter(path)

    def translate(self, file_name):
        self.parser = Parser.Parser(self.input_file_path)
        while self.parser.has_more_commands():
            self.parser.advance()
            self._gen_command()
        self.code_writer.close()

    def _get_number_of_arguments(self, command_type):
        if command_type == Parser.C_PUSH or command_type == Parser.C_POP:
            return 2
        if command_type == Parser.C_ARITHMETIC:
            return 0
        return 0

    def _gen_command(self):
        command_type = self.parser.command_type()
        if command_type == Parser.C_PUSH or command_type == Parser.C_POP:
            self.code_writer.WritePushPop(self.parser.current_commands[0], self.parser.arg1(), self.parser.arg2())
        elif command_type == Parser.C_ARITHMETIC:
            self.code_writer.WriteArithmetic(self.parser.arg1())

def main():
    if not len(sys.argv) == 2:
        print("Usage: assembler.py <input.asm>")
        return
    in_path = sys.argv[1]
    if not os.path.isdir(in_path):
        file_name = os.path.splitext(in_path)[0]
        VMtranslator(in_path).translate(file_name)
        return
    translator = VMtranslator(in_path)
    for file_name in os.listdir(in_path):
        if file_name.endswith(".vm"):
            print(os.path.join(in_path, file_name))
            translator.translate(file_name)

if "__main__" == __name__:
    main()
