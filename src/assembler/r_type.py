#only for logic implementation, code was compiled into one file.

func3 = {"add": "000", "sub": "000", "slt": "010", "srl": "101", "or": "110", "and": "111"}
opcode = {"add": "0110011", "sub": "0110011", "slt": "0110011", "srl": "0110011", "or": "0110011", "and": "0110011"}

registers = {"zero": "00000", "ra": "00001", "sp": "00010", "gp": "00011", "tp": "00100", "t0": "00101", "t1": "00110",
             "t2": "00111", "s0": "01000", "s1": "01001", "a0": "01010", "a1": "01011", "a2": "01100", "a3": "01101",
             "a4": "01110", "a5": "01111", "a6": "10000", "a7": "10001", "s2": "10010", "s3": "10011", "s4": "10100",
             "s5": "10101", "s6": "10110", "s7": "10111", "s8": "11000", "s9": "11001", "s10": "11010", "s11": "11011",
             "t3": "11100", "t4": "11101", "t5": "11110", "t6": "11111"}

def validate_r_type(parts):
    if len(parts) != 4:
        raise ValueError("syntax error, r type needs 3 operands")
    if parts[1] not in registers or parts[2] not in registers or parts[3] not in registers:
        raise ValueError("invalid register")
    if parts[0] not in func3:
        raise ValueError("intstruction not recongnised")

def convert_r_type(parts):
    validate_r_type(parts)
    rd = registers[parts[1]]
    rs1 = registers[parts[2]]
    rs2 = registers[parts[3]]
    funct7 = "0100000" if parts[0] == "sub" else "0000000"
    return f"{funct7}{rs2}{rs1}{func3[parts[0]]}{rd}{opcode[parts[0]]}"

def main():
    instructions = ["add ra, sp, gp", "sub a0, a1, a2"]
    for inst in instructions:
        parts = inst.replace(',', '').split()
        try:
            print(convert_r_type(parts))
        except ValueError as e:
            print(f"Error: {e}")

main()

