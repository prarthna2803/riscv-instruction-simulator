from .tables import opcode, registers
from .utils import int_to_bin


def convert_j_type(op, parts, current_address, labels):
    rd = registers[parts[1]]
    target = parts[2]

    # Calculate offset
    if target.isdigit() or (target[0] == '-' and target[1:].isdigit()):
        offset = int(target) # Direct offset value
    else:
        if target not in labels:
            return None
        offset = labels[target] - current_address # PC-relative offset

    # Convert offset to bits
    imm_bin = int_to_bin(offset, 21) # J-type uses 21-bit immediate

    # Rearrange immediate bits for J-type format
    imm_20 = imm_bin[0]       # bit 20
    imm_10_1 = imm_bin[10:20]  # bits 10-1
    imm_11 = imm_bin[9]        # bit 11
    imm_19_12 = imm_bin[1:9]   # bits 19-12

    op_val = opcode["J-Type"][op]

    return f"{imm_20}{imm_10_1}{imm_11}{imm_19_12}{rd}{op_val}"

