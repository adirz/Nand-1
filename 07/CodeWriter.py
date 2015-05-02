import os
ARITH_COMMANDS = ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]
COMMANDS = ["push", "pop", "label", "goto", "if-goto", "function", "return", "call"]

STACK_BASE_ADDRESS = 256
REGISTERS_BASE_ADDRESS = 0
LCL = 1
ARG = 2
THIS = 3
THAT = 4
TEMP = 5
REG = 13
STATIC_BASE_ADDRESS = 16
STACK_BASE_ADDRESS = 256
HEAP_BASE_ADDRESS = 2048
MEM_IO_BASE_ADDRESS = 16384

class CodeWriter(object):

    def __init__(self, output_file_path):
        self._output_file = open(output_file_path, "w")
        self._file_name = os.path.basename(os.path.splitext(output_file_path)[0])
        self._a_instruction(str(STACK_BASE_ADDRESS))
        self._c_instruction("D", "A")
        self._set_var("SP")
        self._label_count = 1

    #setting a variable with name
    def _set_var(self, symbol):
        self._a_instruction(symbol)
        self._c_instruction("M", "D")

    #write a instruction to this adress
    def _a_instruction(self, address):
        self._output_file.write("@" + address + "\n")

    def _c_instruction(self, dest, comp, jump = None):
        if dest is not None:
            self._output_file.write(dest + "=")
        self._output_file.write(comp)
        if jump is not None:
            self._output_file.write(";" + jump)
        self._output_file.write("\n")

    def _w_label(self, symbol):
        self._output_file.write("(" + symbol + ")\n")

    #retrieving wht in SP to A
    def _get_sp(self):
        self._a_instruction("SP")
        self._c_instruction("A", "M")

    #popping from stack to dest
    def _pop_to_dest(self, dest):
        self._a_instruction("SP")
        self._c_instruction("M", "M-1")
        self._get_sp()
        self._c_instruction(dest, "M")

    #pushing from dest to stack
    def _push_dest(self, dest):
        self._get_sp()
        self._c_instruction("M", dest)
        self._a_instruction("SP")
        self._c_instruction("M", "M+1")

    #comands using two argument
    def _binary_command(self, action):
        self._output_file.write("\n")
        self._pop_to_dest("D")
        self._pop_to_dest("A")
        self._c_instruction("D", "A" + action + "D")
        self._push_dest("D")
        self._output_file.write("\n")

    #comands using one argument
    def _unary_command(self, comp):
        self._output_file.write("\n")
        self._pop_to_dest("A")
        self._c_instruction("D", comp + "A")
        self._push_dest("D")
        self._output_file.write("\n")

    #in case of comp use jump
    def _jump(self, comp, jump):
        self._label_count += 1
        self._a_instruction("LBL" + str(self._label_count))
        self._c_instruction(None, comp, jump)
        return "LBL" + str(self._label_count)

    #commands using jumps
    def _compare_command(self, action):
        self._output_file.write("\n")
        self._pop_to_dest("D")
        self._pop_to_dest("A")
        #checking if the signs are different
        self._c_instruction("D", "A-D") # putting their diference in D
        self._push_dest("-1")
        true_jump_lable = self._jump("D", action)   #jump to true label if true
        #else does the following code-putting 0 in the stack
        self._a_instruction("SP")
        self._c_instruction("M", "M-1")
        self._push_dest("0")
        self._w_label(true_jump_lable)    #true label where to skip to
        self._output_file.write("\n")

    #by the given command_type call the correct writer function
    def write_arithmetic(self, command_type):
        self._output_file.write("\n")
        func, arg = {
            "add"   : [self._binary_command,    "+"],
            "sub"   : [self._binary_command,    "-"],
            "neg"   : [self._unary_command,     "-"],
            "eq"    : [self._compare_command,   "JEQ"],
            "gt"    : [self._compare_command,   "JGT"],
            "lt"    : [self._compare_command,   "JLT"],
            "and"   : [self._binary_command,    "&"],
            "or"    : [self._binary_command,    "|"],
            "not"   : [self._unary_command,     "!"]
        }[command_type]
        func(arg)
        self._output_file.write("\n")

    #a coomon between some push commands
    def _push_regs(self, segment, index):
        self._a_instruction(segment)
        self._c_instruction("D", "M")
        self._a_instruction(str(index))
        self._c_instruction("A", "A+D")
        self._c_instruction("D", "M")

    #a coomon between some pop commands
    def _pop_regs(self, segment, index):
        self._a_instruction(segment)
        self._c_instruction("D", "M")
        self._a_instruction(str(index))
        self._c_instruction("D", "A+D")
        self._set_var("R"+str(REG))

    #by the given command, segment, index call the correct writer function
    def write_push_pop(self, command, segment, index):
        self._output_file.write("\n")
        if command == "push":
            if segment == "argument" :
                self._push_regs(str(ARG), index)
            elif segment == "local":
                self._push_regs(str(LCL), index)
            elif segment == "static":
                self._a_instruction(self._file_name + str(index))
                self._c_instruction("D", "M")
            elif segment == "constant":
                self._a_instruction(str(index))
                self._c_instruction("D", "A")
            elif segment == "this":
                self._push_regs(str(THIS), index)
            elif segment == "that":
                self._push_regs(str(THAT), index)
            elif segment == "pointer":
                self._a_instruction(str(THIS + index))
                self._c_instruction("D", "M")
            elif segment == "temp":
                self._a_instruction(str(TEMP + index))
                self._c_instruction("D", "M")
            self._push_dest("D")
        elif command == "pop":
            if segment == "argument":
                self._pop_regs(str(ARG), str(index))
            elif segment == "local":
                self._pop_regs(str(LCL), str(index))
            elif segment == "static":
                self._a_instruction(self._file_name+str(index))
                self._c_instruction("D", "A")
                self._set_var("R"+str(REG))
            elif segment == "this":
                self._pop_regs(str(THIS), str(index))
            elif segment == "that":
                self._pop_regs(str(THAT), str(index))
            elif segment == "pointer":
                self._a_instruction(str(THIS + index))
                self._c_instruction("D", "A")
                self._set_var("R"+str(REG))
            elif segment == "temp":
                self._a_instruction(str(TEMP + index))
                self._c_instruction("D", "A")
                self._set_var("R"+str(REG))
            self._pop_to_dest("D")
            self._a_instruction("R"+str(REG))
            self._c_instruction("A", "M")
            self._c_instruction("M", "D")
        self._output_file.write("\n")

    #closing the file we written
    def close(self):
        self._output_file.close()
