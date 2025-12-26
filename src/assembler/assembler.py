from .r_type import convert_r_type
from .i_type import convert_i_type

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

def validate_instruction(op, parts):
    # Instruction Error: Check if the instruction is recognized
    if op not in func3["R-Type"] and op not in func3["I-Type"] and op not in func3["S-Type"] and op not in func3["B-Type"] and op not in func3["J-Type"]:
        raise ValueError(f"Unrecognized instruction: {op}")

    # Syntax Error: Check if the correct number of arguments is provided
    expected_args = {"R-Type": 4,"I-Type": 4,"S-Type": 4,"B-Type": 4,"J-Type": 3}

    for inst_type, count in expected_args.items():
        if op in func3[inst_type] and len(parts) != count:
            raise ValueError(f"Syntax error: Incorrect number of arguments for {op}, expected {count}")

    # Register Error: Check if the provided registers exist
    if op in func3["R-Type"]:
        if parts[1] not in registers or parts[2] not in registers or parts[3] not in registers:
            raise ValueError(f"Invalid register in {op} instruction")
    elif op in func3["I-Type"]:
        if parts[1] not in registers or parts[2] not in registers:
            raise ValueError(f"Invalid register in {op} instruction")
    elif op in func3["S-Type"]:
        if parts[1] not in registers or parts[3] not in registers:
            raise ValueError(f"Invalid register in {op} instruction")
    elif op in func3["B-Type"]:
        if parts[1] not in registers or parts[2] not in registers:
            raise ValueError(f"Invalid register in {op} instruction")
    elif op in func3["J-Type"]:
        if parts[1] not in registers:
            raise ValueError(f"Invalid register in {op} instruction")

    # Immediate Value Error: Check if the immediate value is within the allowed range
    def check_immediate(imm, bits, signed=True):
        min_val = - (1 << (bits - 1)) if signed else 0
        max_val = (1 << (bits - 1)) - 1 if signed else (1 << bits) - 1
        if not (min_val <= imm <= max_val):
            raise ValueError(f"Immediate value {imm} out of range for {bits}-bit field: [{min_val}, {max_val}]")

    try:
        if op in func3["I-Type"]:
            imm = int(parts[3])  
            check_immediate(imm, 12)  

        elif op in func3["S-Type"]:
            imm = int(parts[2])  
            check_immediate(imm, 12)  

        elif op in func3["B-Type"]:
            if parts[3].isdigit():
                imm = int(parts[3])  
                check_immediate(imm, 13) 

        elif op in func3["J-Type"]:
            if parts[2].isdigit():
                imm = int(parts[2])  
                check_immediate(imm, 21)  

    except ValueError:
        raise ValueError(f"Invalid immediate value in {op} instruction")


def convert_i_type(op, parts):
    rd = registers[parts[1]]
    rs1 = registers[parts[2]]
    imm = int(parts[3])
    imm_val = int_to_bin(imm, 12)
    funct3_val = func3["I-Type"][op]
    op_val = opcode["I-Type"][op]
    return f"{imm_val}{rs1}{funct3_val}{rd}{op_val}"

def convert_s_type(op, parts):
    rs2 = registers[parts[1]]
    imm = int(parts[2])
    rs1 = registers[parts[3]]
    imm_val = int_to_bin(imm, 12)
    funct3_val = func3["S-Type"][op]
    op_val = opcode["S-Type"][op]
    return f"{imm_val[:7]}{rs2}{rs1}{funct3_val}{imm_val[7:]}{op_val}"

def convert_b_type(op, parts, current_address, labels):
    rs1 = registers[parts[1]]
    rs2 = registers[parts[2]]
    target = parts[3]
    
    # Handle label or immediate
    if target.isdigit() or (target[0] == '-' and target[1:].isdigit()):
        offset = int(target) * 2  # Convert immediate to byte offset
    else:
        if target not in labels:
            return None  # Skip this instruction for now
        offset = (labels[target] - current_address)
    
    imm = offset // 2
    imm_bin = int_to_bin(imm, 13)
    funct3_val = func3["B-Type"][op]
    op_val = opcode["B-Type"][op]
    
    # Rearrange immediate bits for B-type format
    imm_12 = imm_bin[0]
    imm_11 = imm_bin[1]
    imm_10_5 = imm_bin[2:8]
    imm_4_1 = imm_bin[8:12]
    
    return f"{imm_12}{imm_10_5}{rs2}{rs1}{funct3_val}{imm_4_1}{imm_11}{op_val}"

def convert_j_type(op, parts, current_address, labels):
    rd = registers[parts[1]]
    target = parts[2]
    
    # Handle label or immediate
    if target.isdigit() or (target[0] == '-' and target[1:].isdigit()):
        offset = int(target) * 2  # Convert immediate to byte offset
    else:
        if target not in labels:
            return None  # Skip this instruction for now
        offset = (labels[target] - current_address)
    
    imm = offset // 2
    imm_bin = int_to_bin(imm, 21)
    op_val = opcode["J-Type"][op]
    imm_20 = imm_bin[0]       
    imm_10_1 = imm_bin[10:20]  
    imm_11 = imm_bin[9]        
    imm_19_12 = imm_bin[1:9]   
    return f"{imm_20}{imm_10_1}{imm_11}{imm_19_12}{rd}{op_val}"

def convert_to_binary(instruction, labels, current_address):
    parts = instruction.replace(',', ' ').replace("(", ' ').replace(")", "").split()
    op = parts[0]
    validate_instruction(op,parts)
    if op in func3["R-Type"]:
        return convert_r_type(op, parts)
    elif op in func3["I-Type"]:
        return convert_i_type(op, parts)
    elif op in func3["S-Type"]:
        return convert_s_type(op, parts)
    elif op in func3["B-Type"]:
        return convert_b_type(op, parts, current_address, labels)
    elif op in func3["J-Type"]:
        return convert_j_type(op, parts, current_address, labels)
    else:
        raise ValueError(f"Unsupported instruction: {op}")

def main():
    # First pass: collect labels
    instructions = []
    labels = {}
    current_address = 0
    
    with open("input_file.txt", "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            if ':' in line:
                label, instruction = line.split(':')
                labels[label.strip()] = current_address
                if instruction.strip():
                    instructions.append((instruction.strip(), current_address))
                    current_address += 4
            else:
                instructions.append((line, current_address))
                current_address += 4
    
    # Second pass: convert instructions
    for instruction, addr in instructions:
        try:
            binary = convert_to_binary(instruction, labels, addr)
            if binary:  # Only print if conversion was successful
                print(f"{binary}")
        except Exception as e:
            print(f"Error processing line: {instruction} -> {e}")

main()
