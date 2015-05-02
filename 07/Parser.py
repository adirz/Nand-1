ARITH_COMMANDS = ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]

C_PUSH          = "C_PUSH"
C_POP           = "C_POP"
C_LABEL         = "C_LABEL"
C_GOTO          = "C_GOTO"
C_IF            = "C_IF"
C_FUNCTION      = "C_FUNCTION"
C_RETURN        = "C_RETURN"
C_CALL          = "C_CALL"
C_ARITHMETIC    = "C_ARITHMETIC"

COMMANDS = {
                "push"      : C_PUSH,
                "pop"       : C_POP,
                "label"     : C_LABEL,
                "goto"      : C_GOTO,
                "if-goto"   : C_IF,
                "function"  : C_FUNCTION,
                "return"    : C_RETURN,
                "call"      : C_CALL
            }

COMMENT_PREFIX = "//"

"""
Parse the input vm file, line by line.
Used by the VMtranslator object, which does a double pass over the file.
Cleans comments and can get mnemonic from a command and the type of a command
"""
class Parser(object):

    def __init__(self, input_file_path):
        with open(input_file_path, 'r') as input_file:
            self.temp_lines = input_file.readlines()
        self._current_line_index = -1
        self._clear_lines()

    def has_more_commands(self):
        return self._current_line_index < len(self.lines) -1

    def _clear_lines(self):
        cleared_lines = []
        for line in self.temp_lines:
            cleared_line = self._clear_line(line)
            if cleared_line is not "" and cleared_line is not "\n":
                cleared_lines.append(cleared_line)
        self.lines = cleared_lines

    def _clear_line(self, line):
        return line.split(COMMENT_PREFIX)[0].replace("\n","")

    def _line_to_command(self, line):
        return line.split(" ")

    def advance(self):
        self._current_line_index += 1
        self.current_commands = self._line_to_command(self.lines[self._current_line_index])

    def command_type(self):
        if self.current_commands[0] in ARITH_COMMANDS:
            return C_ARITHMETIC
        return COMMANDS[self.current_commands[0]]

    def arg1(self):
        if self.command_type() == C_ARITHMETIC:
            return self.current_commands[0]
        return self.current_commands[1]

    def arg2(self):
        return int(self.current_commands[2])
