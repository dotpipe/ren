import sys

def compress_32bits(data):
    compressed = ""
    i = 0
    while i < len(data):
        if data[i:i+3] == "011": compressed += "5"; i += 3
        elif data[i:i+3] == "010": compressed += "4"; i += 3
        elif data[i:i+3] == "000": compressed += "2"; i += 3
        elif data[i:i+3] == "110": compressed += "1"; i += 3
        elif data[i:i+3] == "111": compressed += "6"; i += 3
        elif data[i:i+3] == "101": compressed += "3"; i += 3
        elif data[i:i+3] == "001": compressed += "0"; i += 3
        else: compressed += data[i]; i += 1
    binary_compressed = ''.join(format(int(digit), '04b') for digit in compressed)
    return binary_compressed

def decompress_32bits(compressed):
    decompression_map = {
        "7": "111", "5": "011", "4": "010",
        "2": "000", "1": "110", "6": "111",
        "3": "101", "0": "001"
    }
    decompressed = ""
    for digit in compressed:
        decompressed += decompression_map.get(digit, digit)
    return decompressed

def compress_verify(data, passes):
    original = data
    for p in range(passes):
        compressed = compress_32bits(data)
        decompressed = decompress_32bits(compressed)
        
        # Pad the shorter string with zeros for comparison
        max_len = max(len(original), len(decompressed))
        original_padded = original.ljust(max_len, '0')
        decompressed_padded = decompressed.ljust(max_len, '0')
        
        if original_padded != decompressed_padded:
            print(f"Verification failed at pass {p+1}")
            print(f"Original:    {original_padded}")
            print(f"Decompressed: {decompressed_padded}")
            print(f"Difference at index: {next(i for i in range(max_len) if original_padded[i] != decompressed_padded[i])}")
            return compressed  # Return the compressed data even if verification fails
        
        data = compressed
    return data


def decompress_multi(compressed, passes):
    for _ in range(passes):
        compressed = decompress_32bits(compressed)
    return compressed

def process_file(input_file, output_file, mode, passes):
    with open(input_file, 'rb') as f:
        data = f.read()
    
    binary_data = ''.join(format(byte, '08b') for byte in data)
    
    if mode == "compress":
        compressed_chunks = []
        for i in range(0, len(binary_data), 32):
            chunk = binary_data[i:i+32]
            compressed = compress_verify(chunk, passes)
            compressed_chunks.append(compressed)
        result = ''.join(compressed_chunks)
    else:  # decompress
        decompressed_chunks = []
        for i in range(0, len(binary_data), 32):
            chunk = binary_data[i:i+32]
            decompressed = decompress_multi(chunk, passes)
            decompressed_chunks.append(decompressed)
        result = ''.join(decompressed_chunks)
    
    output_bytes = int(result, 2).to_bytes((len(result) + 7) // 8, byteorder='big')
    
    with open(output_file, 'wb') as f:
        f.write(output_bytes)
    
    print(f"{'Compressed' if mode == 'compress' else 'Decompressed'} data saved to {output_file}")
    print(f"Original size: {len(data)} bytes")
    print(f"{'Compressed' if mode == 'compress' else 'Decompressed'} size: {len(output_bytes)} bytes")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python script.py [compress/decompress] [input_file] [output_file] [passes]")
        sys.exit(1)

    mode = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3]
    passes = int(sys.argv[4])

    if mode not in ["compress", "decompress"]:
        print("Invalid mode. Use 'compress' or 'decompress'.")
        sys.exit(1)

    process_file(input_file, output_file, mode, passes)