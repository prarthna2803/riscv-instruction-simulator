registers = [0] * 32  
memory = {} 
PC = 0x0 
OUTPUT_FILE = "output.txt"

with open(OUTPUT_FILE, 'w') as f:
    f.write("")

def sign_extend(value, bits):
    sign_bit = 1 << (bits - 1)
    return (value & (sign_bit - 1)) - (value & sign_bit)

def write_state():
    with open(OUTPUT_FILE, 'a') as f:
        f.write(f"0b{PC:032b} ")
        for reg in registers:
            f.write(f"0b{reg:032b} ")
        f.write("\n")

def execute_instruction(instr):
    global PC, registers

    opcode = int(instr[25:32], 2)
    rd = int(instr[20:25], 2)
    funct3 = int(instr[17:20], 2)
    rs1 = int(instr[12:17], 2)
    rs2 = int(instr[7:12], 2)
    funct7 = int(instr[0:7], 2)
    registers[0] = 0  

    if opcode == 0b0110011:
        if funct3== 0b000: #plus or minus
            if funct7 == 0b0000000: #ADD
                registers[rd] = registers[rs1] + registers[rs2] & 0xFFFFFFFF
            elif funct7 == 0b0100000: #SUB
                registers[rd] = registers[rs1] - registers[rs2] & 0xFFFFFFFF

        elif funct3 == 0b010: #SLT
            registers[rd] = 1 if registers[rs1] < registers[rs2] else 0
        elif funct3 == 0b101 and funct7==0b0000000: #SRL
            registers[rd] = (registers[rs1] >> registers[rs2]) & 0xFFFFFFFF
        elif funct3 == 0b110:  # OR
            registers[rd] = (registers[rs1] | registers[rs2]) & 0xFFFFFFFF

        elif funct3 == 0b111:  # AND
            registers[rd] = (registers[rs1] & registers[rs2] )& 0xFFFFFFFF
        
        PC += 4

    write_state()

def write_memory():
    with open(OUTPUT_FILE, 'a') as f:
        for addr in range(0x00010000, 0x00010080, 4):
            value = memory.get(addr, 0)
            f.write(f"0x{addr:08X}:0b{value:032b}\n")

def main():
    with open("file_2.txt", "r") as file:
        for line in file:
            execute_instruction(line.strip())

    write_memory()
    print(f"output saved to '{OUTPUT_FILE}'")

main()
