def compress_56bits(data):
    compressed = ""
    i = 0
    while i < len(data):
        if data[i:i+8] == "111111": compressed += "3"; i += 6
        elif data[i:i+6] == "1111": compressed += "7"; i += 4
        elif data[i:i+8] == "010101": compressed += "5"; i += 6
        elif data[i:i+6] == "0101": compressed += "4"; i += 4
        elif data[i:i+8] == "000000": compressed += "1"; i += 6
        elif data[i:i+6] == "0000": compressed += "0"; i += 4
        elif data[i:i+4] == "11": compressed += "2"; i += 2
        elif data[i:i+4] == "01": compressed += "6"; i += 2
        else: compressed += "9" + data[i]; i += 1
    return compressed

def decompress_56bits(compressed):
    decompressed = ""
    i = 0
    while i < len(compressed):
        if compressed[i] == "3": decompressed += "111111"
        elif compressed[i] == "5": decompressed += "010101"
        elif compressed[i] == "4": decompressed += "0101"
        elif compressed[i] == "2": decompressed += "000000"
        elif compressed[i] == "1": decompressed += "0000"
        elif compressed[i] == "7": decompressed += "1111"
        elif compressed[i] == "0": decompressed += "01"
        elif compressed[i] == "9":
            i += 1
            decompressed += compressed[i]
        i += 1
    return decompressed

def process_file(input_file, output_file, mode):
    with open(input_file, 'rb') as f:
        data = f.read()
    
    binary_data = ''.join(format(byte, '08b') for byte in data)
    
    if mode == "compress":
        compressed_chunks = []
        passes_list = []
        for i in range(0, len(binary_data), 56):
            chunk = binary_data[i:i+56].ljust(56, '0')
            compressed = chunk
            passes = 0
            while len(compressed) > 1 and passes < 248:
                next_compressed = compress_56bits(compressed)
                if len(next_compressed) >= len(compressed):
                    break
                compressed = next_compressed
                passes += 1
            compressed_chunks.append(compressed)
            passes_list.append(passes)
        result = ''.join(f"{256-passes:08b}{chunk}" for passes, chunk in zip(passes_list, compressed_chunks))
    else:  # decompress
        result = ""
        for i in range(0, len(binary_data), 64):  # 8 bits for passes + 56 bits of data
            chunk = binary_data[i:i+64]
            passes = 256 - int(chunk[:8], 2)
            compressed = chunk[8:]
            decompressed = compressed
            for _ in range(passes):
                decompressed = decompress_56bits(decompressed)
            result += decompressed

    result = ''.join(char for char in result if char in '01')
    output_bytes = int(result, 2).to_bytes((len(result) + 7) // 8, byteorder='big')
    # output_bytes = int(result, 2).to_bytes((len(result) + 7) // 8, byteorder='big')

    with open(output_file, 'wb') as f:
        f.write(output_bytes)
    
    print(f"{'Compressed' if mode == 'compress' else 'Decompressed'} data saved to {output_file}")
    print(f"Original size: {len(data)} bytes")
    print(f"{'Compressed' if mode == 'compress' else 'Decompressed'} size: {len(output_bytes)} bytes")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python script.py [compress/decompress] [input_file] [output_file]")
        sys.exit(1)

    mode = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3]

    if mode not in ["compress", "decompress"]:
        print("Invalid mode. Use 'compress' or 'decompress'.")
        sys.exit(1)

    process_file(input_file, output_file, mode)
