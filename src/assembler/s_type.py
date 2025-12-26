from .tables import func3, opcode, registers
from .utils import int_to_bin


def convert_s_type(op, parts):
  # Parse the offset and base register from the format: offset(reg)
    rs2 = registers[parts[1]] # Source register
    offset_str, base_reg = parts[2].split('(')
    base_reg = base_reg.rstrip(')')
    imm = int(offset_str)
    rs1 = registers[base_reg] # Base register

    imm_val = int_to_bin(imm, 12)
    # S-type immediate is split into two parts
    imm_11_5 = imm_val[:7] # Upper 7 bits
    imm_4_0 = imm_val[7:] # Lower 5 bits

    funct3_val = func3["S-Type"][op]
    op_val = opcode["S-Type"][op]

    return f"{imm_11_5}{rs2}{rs1}{funct3_val}{imm_4_0}{op_val}"

