import sys
memory = {}
reg = [0] * 32
reg[2] = 380  #register 2 is sp (initialized to 380)
PC = 0

INPUT_FILE = str(sys.argv[1]) 
OUTPUT_FILE = str(sys.argv[2])

def sign_extend(value, bits):
    sign_bit = 1 << (bits - 1)
    return (value & (sign_bit - 1)) - (value & sign_bit)

def write_memory():
    with open(OUTPUT_FILE, 'a') as f:
        for addr in range(0x00010000, 0x00010080, 4):
            value = memory.get(addr, 0)
            f.write(f"0x{addr:08X}:0b{value:032b}\n")

def write_state():
    with open(OUTPUT_FILE, 'a') as f:
        f.write(f"0b{PC:032b} ")
        for r in reg:
            f.write(f"0b{r:032b} ")
        f.write("\n")

def btype(i):
    funct3 = i[17:20]
    rs1 = int(i[12:17], 2)
    rs2 = int(i[7:12], 2)

    if funct3 == '000':  # BEQ
        return reg[rs1] == reg[rs2]
    elif funct3 == '001':  # BNE
        return reg[rs1] != reg[rs2]
    return False

def get_btype_imm(i):
    imm = i[0] + i[24] + i[1:7] + i[20:24]
    imm = int(imm, 2)
    return sign_extend(imm << 1, 13)

def get_jtype_imm(i):
    return sign_extend(int(i[0] + i[12:20] + i[11] + i[1:11] + '0', 2), 21)

# Clear output file
with open(OUTPUT_FILE, 'w') as f:
    f.write("")

# Read input instructions
with open(INPUT_FILE, 'r') as f:
    instr = f.read().strip().splitlines()

pointer = 0
while 0 <= pointer < len(instr):
    i = instr[pointer]
    opcode = int(i[25:32], 2)

    if opcode == 0b1100011:  # B-TYPE
        imm = get_btype_imm(i)
        if btype(i):
            if imm == 0 and i[12:17] == "00000" and i[7:12] == "00000":
                write_state()
                break  # Virtual halt
            pointer += imm // 4
            PC += imm
        else:
            pointer += 1
            PC += 4

    elif opcode == 0b1101111:  # J-TYPE
        rd = int(i[20:25], 2)
        imm = get_jtype_imm(i)
        reg[rd] = PC + 4
        pointer += imm // 4
        PC += imm

    elif opcode == 0b1100111:  # JALR
        rd = int(i[20:25], 2)
        rs1 = int(i[12:17], 2)
        imm = sign_extend(int(i[0:12], 2), 12)
        target = (reg[rs1] + imm) & 0xFFFFFFFE
        reg[rd] = PC + 4
        pointer = target // 4
        PC = target

    elif opcode == 0b0110011:  # R-type
        rd = int(i[20:25], 2)
        funct3 = int(i[17:20], 2)
        rs1 = int(i[12:17], 2)
        rs2 = int(i[7:12], 2)
        funct7 = int(i[0:7], 2)

        if funct3 == 0b000:
            if funct7 == 0b0000000:  # ADD
                reg[rd] = (reg[rs1] + reg[rs2]) & 0xFFFFFFFF
            elif funct7 == 0b0100000:  # SUB
                reg[rd] = (reg[rs1] - reg[rs2]) & 0xFFFFFFFF
        elif funct3 == 0b010:  # SLT
            reg[rd] = int(reg[rs1] < reg[rs2])
        elif funct3 == 0b101 and funct7 == 0b0000000:  # SRL
            reg[rd] = (reg[rs1] >> reg[rs2]) & 0xFFFFFFFF
        elif funct3 == 0b110:  # OR
            reg[rd] = (reg[rs1] | reg[rs2]) & 0xFFFFFFFF
        elif funct3 == 0b111:  # AND
            reg[rd] = (reg[rs1] & reg[rs2]) & 0xFFFFFFFF

        reg[0] = 0
        pointer += 1
        PC += 4

    elif opcode == 0b0010011:  # I-type
        rd = int(i[20:25], 2)
        funct3 = int(i[17:20], 2)
        rs1 = int(i[12:17], 2)
        imm = sign_extend(int(i[0:12], 2), 12)
        if funct3 == 0b000:  # ADDI
            reg[rd] = (reg[rs1] + imm) & 0xFFFFFFFF
        reg[0] = 0
        pointer += 1
        PC += 4

    elif opcode == 0b0000011:  # LW
        rd = int(i[20:25], 2)
        rs1 = int(i[12:17], 2)
        imm = sign_extend(int(i[0:12], 2), 12)
        addr = (reg[rs1] + imm) & 0xFFFFFFFF
        reg[rd] = memory.get(addr, 0)
        pointer += 1
        PC += 4

    elif opcode == 0b0100011:  # SW
        rs2 = int(i[7:12], 2)
        rs1 = int(i[12:17], 2)
        funct3 = int(i[17:20], 2)
        imm = i[0:7] + i[20:25]
        imm = sign_extend(int(imm, 2), 12)
        if funct3 == 0b010:
            addr = (reg[rs1] + imm) & 0xFFFFFFFF
            memory[addr] = reg[rs2]
        pointer += 1
        PC += 4

    else:
        print(f"[ERROR] Unsupported opcode: {opcode:07b}")
        break
    reg[0] = 0
    write_state()  # write memory state
write_memory()
