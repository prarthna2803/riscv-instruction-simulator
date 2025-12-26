from .tables import func3, opcode, registers


def convert_r_type(op, parts):
    rd = registers[parts[1]]
    rs1 = registers[parts[2]]
    rs2 = registers[parts[3]]

    funct7 = "0100000" if op == "sub" else "0000000"
    funct3_val = func3["R-Type"][op]
    op_val = opcode["R-Type"][op]

    return f"{funct7}{rs2}{rs1}{funct3_val}{rd}{op_val}"
