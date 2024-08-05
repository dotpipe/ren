def compress_56bits(data):
    compressed = ""
    i = 0
    while i < len(data):
        if data[i:i+6] == "111111":
            compressed += "8"
            i += 6
        elif data[i:i+4] == "1111":
            compressed += "7"
            i += 4
        elif data[i:i+6] == "010101":
            compressed += "5"
            i += 6
        elif data[i:i+4] == "0101":
            compressed += "4"
            i += 4
        elif data[i:i+6] == "000000":
            compressed += "2"
            i += 6
        elif data[i:i+4] == "0000":
            compressed += "1"
            i += 4
        elif data[i:i+2] == "10":
            compressed += "9"
            i += 2
        elif data[i:i+2] == "01":
            compressed += "3"
            i += 2
        elif data[i:i+2] == "00":
            compressed += "0"
            i += 2
        else:
            compressed += "6" + data[i]
            i += 1
    return compressed

def decompress_56bits(compressed):
    decompression_map = {
        "8": "111111", "7": "1111", "5": "010101", "4": "0101",
        "2": "000000", "1": "0000", "9": "10", "3": "01", "0": "00"
    }
    decompressed = ""
    i = 0
    while i < len(compressed):
        if compressed[i] in decompression_map:
            decompressed += decompression_map[compressed[i]]
        elif compressed[i] == "6":
            if i + 1 < len(compressed):
                i += 1
                decompressed += compressed[i]
            else:
                raise ValueError("Unexpected end of input after '6' marker")
        else:
            decompressed += compressed[i]
        i += 1
    return decompressed

def decompress_fully(compressed, passes):
    decompressed = compressed
    # print("{} passes".format(passes))
    for _ in range(passes):
        decompressed = decompress_56bits(decompressed)
    return decompressed

def compress_fully(data):
    passes = 0
    while len(data) > 1:
        next_compressed = compress_56bits(data)
        if len(next_compressed) >= len(data):
            break
        data = next_compressed
        passes += 1
    # print("{} passes".format(passes))
    return data, passes

def process_file(input_file, output_file, mode):
    with open(input_file, 'rb') as f:
        data = f.read()
    
    binary_data = ''.join(format(byte, '08b') for byte in data)
    
    if mode == "compress":
        compressed_chunks = []
        passes_list = []
        for i in range(0, len(binary_data), 56):
            chunk = binary_data[i:i+56].ljust(56, '0')
            compressed, passes = compress_fully(chunk)
            if verify_compression(chunk):
                compressed_chunks.append(compressed)
                passes_list.append(passes)
            else:
                print(f"Verification failed for chunk starting at index {i}")
        result = ''.join(f"{chunk}{256-passes:08b}" for chunk, passes in zip(compressed_chunks, passes_list))
    else:  # decompress
        result = ""
        for i in range(0, len(binary_data), 64):
            chunk = binary_data[i:i+64]
            data = int(chunk[:56], 2)
            passes = int(chunk[56:], 2)
            decompressed = decompress_fully(data, passes)
            result += decompressed

    result = ''.join(char for char in result if char in '01')
    output_bytes = int(result, 2).to_bytes((len(result) + 7) // 8, byteorder='big')

    with open(output_file, 'wb') as f:
        f.write(output_bytes)
    
    print(f"{'Compressed' if mode == 'compress' else 'Decompressed'} data saved to {output_file}")
    print(f"Original size: {len(data)} bytes")
    print(f"{'Compressed' if mode == 'compress' else 'Decompressed'} size: {len(output_bytes)} bytes")

def verify_compression(data):
    compressed = compress_fully(data)
    decompressed = decompress_fully(compressed[0], compressed[1])
    print(data == decompressed)
    return data == decompressed

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