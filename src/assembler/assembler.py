import sys

from .r_type import convert_r_type
from .i_type import convert_i_type
from .s_type import convert_s_type
from .b_type import convert_b_type
from .j_type import convert_j_type
from .tables import func3
from .validate_instr import validate_instruction

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
            return binary if binary is not None else f"UNRESOLVED_B:{op}:{','.join(parts[1:])}"
        elif op in func3["J-Type"]:
            binary = convert_j_type(op, parts, current_address, labels)
            return binary if binary is not None else f"UNRESOLVED_J:{op}:{','.join(parts[1:])}"
    except Exception as e:
        raise ValueError(f"Error in {op} instruction: {str(e)}")
             
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
