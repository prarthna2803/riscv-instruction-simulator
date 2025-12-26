from .tables import func3, opcode, registers
from .utils import int_to_bin


def convert_i_type(op, parts):
    if op == "lw":
        rd = registers[parts[1]]
        offset_str, base_reg = parts[2].split('(')
        base_reg = base_reg.rstrip(')')
        imm = int(offset_str)
        rs1 = registers[base_reg]
        imm_val = int_to_bin(imm, 12)
    else:
        rd = registers[parts[1]]
        rs1 = registers[parts[2]]
        imm = int(parts[3])
        imm_val = int_to_bin(imm, 12)

    funct3_val = func3["I-Type"][op]
    op_val = opcode["I-Type"][op]

    return f"{imm_val}{rs1}{funct3_val}{rd}{op_val}"
