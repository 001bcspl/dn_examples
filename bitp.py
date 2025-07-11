def simple_positions_to_hex():
    """
    Simple version: converts bit positions to 128-bit hex value
    """
    positions_str = input("Enter bit positions (0-127, space-separated): ")
    
    if not positions_str.strip():
        positions = []
    else:
        positions = list(map(int, positions_str.split()))
    
    # Validate positions
    if any(pos < 0 or pos > 127 for pos in positions):
        print("Error: All positions must be between 0 and 127")
        return
    
    # Calculate result
    result = sum(1 << pos for pos in positions)
    
    # Convert to 32-digit hex (128 bits)
    hex_result = f"{result:032X}"
    
    print(f"Hex result: 0x{hex_result}")

if __name__ == "__main__":
    simple_positions_to_hex()
