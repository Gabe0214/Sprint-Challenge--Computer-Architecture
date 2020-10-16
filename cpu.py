"""CPU functionality."""

import sys


HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
RET = 0b00010001
CALL = 0b01010000
ADD = 0b10100000
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.reg[7] = 0xF4
        self.ram = [0] * 256
        self.pc = 0
        self.halted = False
        self.fl = 0b0000000

        self.sp = 7
        self.branch_table = {
            HLT : self.HLT,
            LDI : self.LDI,
            PRN : self.PRN,
            MUL: self.MUL,
            PUSH: self.PUSH,
            POP: self.POP,
            RET: self.RET,
            CALL: self.CALL,
            ADD: self.ADD,
            CMP : self.CMP,
            JMP: self.JMP,
            JEQ: self.JEQ,
            JNE: self.JNE
        }

    def ram_read(self, address):
        # print(self.ram)
        return self.ram[address]


    def ram_write(self, address, value):
        self.ram[address] = value


    def load(self):
        """Load a program into memory."""
        #
        # address = 0
        #
        # # For now, we've just hardcoded a program:
        #
        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]
        #
        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1
        address = 0
        if len(sys.argv) != 2:
            print("usage: ls8.py filename")
            sys.exit(1)

        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    line = line.split('#')
                    val = line[0].strip()

                    if val == '' :
                        continue
                    instuction = int(val, base=2)
                    self.ram[address] = instuction
                    address += 1



        except FileNotFoundError:
            print(f"File not found: {sys.argv[1]}")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc

        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == "CMP":
            "00000LGE"
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def PRN(self,operand_a, operand_b=None):
        print(self.reg[operand_a])
        self.pc += 2

    def LDI(self,operand_a, operand_b):

        self.reg[operand_a] = operand_b
        self.pc += 3

    def HLT(self, operand_a=None, operand_b=None):
        self.halted = True

    def MUL(self,operand_a, operand_b):
        self.alu('MUL', operand_a, operand_b)
        self.pc += 3

    def PUSH(self, opernad_a=None, operand_b=None):
        self.sp -= 1
        self.reg[self.sp] = self.reg[self.ram[self.pc + 1]]
        self.pc += 2

    def POP(self, operand_a=None, operand_b=None):

        self.reg[self.ram[self.pc + 1]] = self.reg[self.sp]

        self.sp += 1

        self.pc += 2

    def CALL(self, operand_a=None, operand_b=None):
        return_addr = self.pc + 2

        self.sp -= 1
        self.ram[self.sp] = return_addr
        reg_num = self.ram[self.pc + 1]
        subrountine_addr = self.reg[reg_num]

        self.pc = subrountine_addr

    def pop_val(self):
        top_stack = self.sp
        value = self.ram[top_stack]

        self.sp += 1

        return value

    def RET(self, operand_a=None, operand_b =None):
        return_addr = self.pop_val()

        self.pc = return_addr

    def ADD(self, operand_a, operand_b):
        # operand_a = self.ram_read(self.pc + 1)
        # operand_b = self.ram_read(self.pc + 2)

        self.alu('ADD', operand_a, operand_b)

        self.pc += 3

    def CMP(self, operand_a, operand_b):
        self.alu("CMP", operand_a, operand_b)
        self.pc += 3

    def JMP(self, operand_a, operand_b=None):
        self.pc = self.reg[operand_a]


    def JEQ(self, operand_a, operand_b=None):
        #1
        if self.fl & 0b1 == 1:
            self.pc = self.reg[operand_a]

        else:
            self.pc += 2

    def JNE(self, operand_a, operand_b=None):
        #0
        if self.fl & 0b1 == 0:
            self.pc = self.reg[operand_a]

        else:
            self.pc += 2




    def run(self):
        """Run the CPU."""

        while not self.halted:
            instruction_to_execute = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            self.branch_table[instruction_to_execute](operand_a, operand_b)





