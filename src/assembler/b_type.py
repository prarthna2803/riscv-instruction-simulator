from .tables import func3, opcode, registers
from .utils import int_to_bin


def convert_b_type(op, parts, current_address, labels):
    rs1 = registers[parts[1]]
    rs2 = registers[parts[2]]
    target = parts[3]

    # Calculate offset
    if target.isdigit() or (target[0] == '-' and target[1:].isdigit()):
        offset = int(target) # Direct offset value
    else:
        if target not in labels:
            return None
        offset = labels[target] - current_address # PC-relative offset

    imm_bin = int_to_bin(offset, 13) # B-type uses 13-bit immediate

    # Rearrange immediate bits for B-type format
    imm_12 = imm_bin[0]
    imm_11 = imm_bin[1]
    imm_10_5 = imm_bin[2:8]
    imm_4_1 = imm_bin[8:12]

    funct3_val = func3["B-Type"][op]
    op_val = opcode["B-Type"][op]

    return f"{imm_12}{imm_10_5}{rs2}{rs1}{funct3_val}{imm_4_1}{imm_11}{op_val}"

