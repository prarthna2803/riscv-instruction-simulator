# Define funct3 and opcode mappings for all instruction types
func3 = {"R-Type": {"add": "000", "sub": "000", "slt": "010", "srl": "101", "or": "110", "and": "111"},
         "I-Type": {"lw": "010", "addi": "000", "jalr": "000"},
         "S-Type": {"sw": "010"},
         "B-Type": {"beq": "000", "bne": "001", "blt": "100"},
         "J-Type": {"jal": "000"}}

opcode = {"R-Type": {"add": "0110011", "sub": "0110011", "slt": "0110011", "srl": "0110011", "or": "0110011", "and": "0110011"},
          "I-Type": {"lw": "0000011", "addi": "0010011", "jalr": "1100111"},
          "S-Type": {"sw": "0100011"},
          "B-Type": {"beq": "1100011", "bne": "1100011", "blt": "1100011"},
          "J-Type": {"jal": "1101111"}}

registers = {"zero": "00000", "ra": "00001", "sp": "00010", "gp": "00011", "tp": "00100", "t0": "00101", "t1": "00110",
             "t2": "00111", "s0": "01000", "s1": "01001", "a0": "01010", "a1": "01011", "a2": "01100", "a3": "01101",
             "a4": "01110", "a5": "01111", "a6": "10000", "a7": "10001", "s2": "10010", "s3": "10011", "s4": "10100",
             "s5": "10101", "s6": "10110", "s7": "10111", "s8": "11000", "s9": "11001", "s10": "11010", "s11": "11011",
             "t3": "11100", "t4": "11101", "t5": "11110", "t6": "11111"}

def int_to_bin(n, bits=12):
    if n < 0:
        n = (1 << bits) + n
    return format(n & ((1 << bits) - 1), f'0{bits}b')
def convert_i_type(op, parts):
    if op == "lw":
        rd = registers[parts[1]]
        # Parse the offset and base register from the format: offset(reg)
        offset_str, base_reg = parts[2].split('(')
        base_reg = base_reg.rstrip(')')
        imm = int(offset_str)
        rs1 = registers[base_reg]
        imm_val = int_to_bin(imm, 12)
        funct3_val = func3["I-Type"][op]
        op_val = opcode["I-Type"][op]
    else:
        rd = registers[parts[1]]
        rs1 = registers[parts[2]]
        imm = int(parts[3])
        imm_val = int_to_bin(imm, 12)
        funct3_val = func3["I-Type"][op]
        op_val = opcode["I-Type"][op]
    return f"{imm_val}{rs1}{funct3_val}{rd}{op_val}"

def convert_to_binary(instruction):
    # Special handling for lw/sw instructions
    if instruction.startswith(('lw', 'sw')):
        parts = instruction.replace(',', ' ').split(None, 2)
    else:
        parts = instruction.replace(',', ' ').replace("(", ' ').replace(")", "").split()
    
    op = parts[0]

# Immediate Value Error: Check if the immediate value is within the allowed range
    def check_immediate(imm, bits, signed=True):
        min_val = -(1 << (bits - 1)) if signed else 0
        max_val = (1 << (bits - 1)) - 1 if signed else (1 << bits) - 1
        if not (min_val <= imm <= max_val):
            raise ValueError(f"Immediate value {imm} out of range for {bits}-bit field: [{min_val}, {max_val}]")

    try:
        if op in func3["I-Type"]:
            if op == "lw":
                # Extract immediate from offset(reg) format
                imm = int(parts[2].split('(')[0])
            else:
                imm = int(parts[3])
            check_immediate(imm, 12)
        elif op in func3["S-Type"]:
            imm = int(parts[2])
            check_immediate(imm, 12)
        elif op in func3["B-Type"]:
            if parts[3].isdigit() or (parts[3][0] == '-' and parts[3][1:].isdigit()):
                imm = int(parts[3])
                check_immediate(imm, 13)
        elif op in func3["J-Type"]:
            if parts[2].isdigit() or (parts[2][0] == '-' and parts[2][1:].isdigit()):
                imm = int(parts[2])
                check_immediate(imm, 21)
    except ValueError as e:
        if not (op in func3["B-Type"] or op in func3["J-Type"]):
            raise ValueError(f"Invalid immediate value in {op} instruction: {str(e)}")
