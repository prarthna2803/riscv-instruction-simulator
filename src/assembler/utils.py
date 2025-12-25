def int_to_bin(n, bits):
    if n < 0:
        n = (1 << bits) + n
    return format(n & ((1 << bits) - 1), f'0{bits}b')

# Immediate Value Error: Check if the immediate value is within the allowed range
def check_immediate(imm, bits, signed=True):
    min_val = -(1 << (bits - 1)) if signed else 0
    max_val = (1 << (bits - 1)) - 1 if signed else (1 << bits) - 1

    if not (min_val <= imm <= max_val):
        raise ValueError(f"Immediate value {imm} out of range for {bits}-bit field: [{min_val}, {max_val}]")
