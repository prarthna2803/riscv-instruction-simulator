import sys

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

    # Modified expected args for lw instruction
    expected_args = {
        "R-Type": 4,
        "I-Type": {"lw": 3, "addi": 4, "jalr": 4},  # lw expects 3 parts due to different parsing
        "S-Type": {"sw":3},
        "B-Type": 4,
        "J-Type": 3
    }
    # Modified syntax check for different instruction types
    if op in func3["I-Type"]:
        expected = expected_args["I-Type"][op]
        if len(parts) != expected:
            raise ValueError(f"Syntax error: Incorrect number of arguments for {op}, expected {expected}")
    elif op in func3["S-Type"]:
        expected = expected_args["S-Type"][op]
        if len(parts) != expected:
            raise ValueError(f"Syntax error: Incorrect number of arguments for {op}, expected {expected}")
    else:
        for inst_type, count in expected_args.items():
            if isinstance(count, dict):
                continue
            if op in func3[inst_type] and len(parts) != count:
                raise ValueError(f"Syntax error: Incorrect number of arguments for {op}, expected {count}")
def convert_r_type(op, parts):
    rd = registers[parts[1]]
    rs1 = registers[parts[2]]
    rs2 = registers[parts[3]]
    funct7 = "0100000" if op == "sub" else "0000000"
    funct3_val = func3["R-Type"][op]
    op_val = opcode["R-Type"][op]
    return f"{funct7}{rs2}{rs1}{funct3_val}{rd}{op_val}"

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

def convert_s_type(op, parts):
    # Parse the offset and base register from the format: offset(reg)
    rs2 = registers[parts[1]]  # Source register
    offset_str, base_reg = parts[2].split('(')
    base_reg = base_reg.rstrip(')')
    imm = int(offset_str)
    rs1 = registers[base_reg]  # Base register
    
    imm_val = int_to_bin(imm, 12)
    funct3_val = func3["S-Type"][op]
    op_val = opcode["S-Type"][op]
    
    # S-type immediate is split into two parts
    imm_11_5 = imm_val[:7]   # Upper 7 bits
    imm_4_0 = imm_val[7:]    # Lower 5 bits
    
    return f"{imm_11_5}{rs2}{rs1}{funct3_val}{imm_4_0}{op_val}"

def convert_b_type(op, parts, current_address, labels):
    rs1 = registers[parts[1]]
    rs2 = registers[parts[2]]
    target = parts[3]
    
    # Calculate offset
    if target.isdigit() or (target[0] == '-' and target[1:].isdigit()):
        offset = int(target)  # Direct offset value
    else:
        if target not in labels:
            return None
        offset = labels[target] - current_address  # PC-relative offset
    
    # Convert offset to bits
    imm_bin = int_to_bin(offset, 13)  # B-type uses 13-bit immediate
    
    # Rearrange immediate bits for B-type format
    imm_12 = imm_bin[0]  # bit 12
    imm_11 = imm_bin[1]  # bit 11
    imm_10_5 = imm_bin[2:8]  # bits 10-5
    imm_4_1 = imm_bin[8:12]  # bits 4-1
    
    funct3_val = func3["B-Type"][op]
    op_val = opcode["B-Type"][op]
    
    return f"{imm_12}{imm_10_5}{rs2}{rs1}{funct3_val}{imm_4_1}{imm_11}{op_val}"

def convert_j_type(op, parts, current_address, labels):
    rd = registers[parts[1]]
    target = parts[2]
    
    # Calculate offset
    if target.isdigit() or (target[0] == '-' and target[1:].isdigit()):
        offset = int(target)  # Direct offset value
    else:
        if target not in labels:
            return None
        offset = labels[target] - current_address  # PC-relative offset
    
    # Convert offset to bits
    imm_bin = int_to_bin(offset, 21)  # J-type uses 21-bit immediate
    
    # Rearrange immediate bits for J-type format
    imm_20 = imm_bin[0]       # bit 20
    imm_10_1 = imm_bin[10:20]  # bits 10-1
    imm_11 = imm_bin[9]        # bit 11
    imm_19_12 = imm_bin[1:9]   # bits 19-12
    
    op_val = opcode["J-Type"][op]
    
    return f"{imm_20}{imm_10_1}{imm_11}{imm_19_12}{rd}{op_val}"

def convert_to_binary(instruction, labels, current_address):
    # Special handling for lw/sw instructions
    if instruction.startswith(('lw', 'sw')):
        parts = instruction.replace(',', ' ').split(None, 2)
    else:
        parts = instruction.replace(',', ' ').replace("(", ' ').replace(")", "").split()
    
    op = parts[0]
    validate_instruction(op, parts)
    
    try:
        if op in func3["R-Type"]:
            return convert_r_type(op, parts)
        elif op in func3["I-Type"]:
            return convert_i_type(op, parts)
        elif op in func3["S-Type"]:
            return convert_s_type(op, parts)
        elif op in func3["B-Type"]:
            binary = convert_b_type(op, parts, current_address, labels)
            if binary is None:
                return f"UNRESOLVED_B:{op}:{','.join(parts[1:])}"
            return binary
        elif op in func3["J-Type"]:
            binary = convert_j_type(op, parts, current_address, labels)
            if binary is None:
                return f"UNRESOLVED_J:{op}:{','.join(parts[1:])}"
            return binary
    except Exception as e:
        raise ValueError(f"Error in {op} instruction: {str(e)}")
    

    # Register Error: Check if the provided registers exist
    if op in func3["R-Type"]:
        if parts[1] not in registers or parts[2] not in registers or parts[3] not in registers:
            raise ValueError(f"Invalid register in {op} instruction")
    elif op in func3["I-Type"]:
        if op == "lw":
            # For lw, check destination register and base register
            if parts[1] not in registers or parts[2].split('(')[1].rstrip(')') not in registers:
                raise ValueError(f"Invalid register in {op} instruction")
        else:
            # For other I-Type instructions
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

def main():
    # First pass: collect labels and instructions
    instructions = []
    labels = {}
    current_address = 0
    input_filename = str(sys.argv[1])
    output_filename = str(sys.argv[2])
    with open(input_filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
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
    
    # Second pass: resolve all instructions
    with open(output_filename, "w") as outfile:
        for instruction, addr in instructions:
            try:
                binary = convert_to_binary(instruction, labels, addr)
                if binary:
                    if binary.startswith("UNRESOLVED"):
                        # Resolve the instruction now that we have all labels
                        _, type, rest = binary.split(":", 2)
                        op, *args = rest.split(",")
                        parts = [op] + args
                        if type == "B":
                            binary = convert_b_type(op, parts, addr, labels)
                        else:  # type == "J"
                            binary = convert_j_type(op, parts, addr, labels)
                    outfile.write(f"{binary}\n")
            except Exception as e:
                outfile.write(f"Error processing line: {instruction} -> {e}\n")

main()
