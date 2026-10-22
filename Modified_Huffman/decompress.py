import ast 

def decompress(filename):
    with open(filename, "rb") as f:
        total_bits = int(f.readline())
        bits_needed = int(f.readline())
        huffman_count = int(f.readline())
        huffman_table = {}
        for _ in range(huffman_count):
            char, code = f.readline().decode().rstrip("\n").rsplit(":", 1)
            char = ast.literal_eval(char)
            huffman_table[char] = code


        vlc_count = int(f.readline())
        vlc_table = {}
        for _ in range(vlc_count):
            char, index = f.readline().decode().rstrip("\n").rsplit(":", 1)
            char = ast.literal_eval(char)
            vlc_table[char] = int(index)


        compressed_data = f.read()


        bits = ""
        for byte in compressed_data:
            bits += f"{byte:08b}"

        bits = bits[:total_bits]



    code_to_symbol = {}
    for char, code in huffman_table.items():
        code_to_symbol[code] = char

    index_to_char = {}
    for char, index in vlc_table.items():
        index_to_char[index] = char

    result = []
    i = 0

    while i < len(bits):
        code = ""

        while i < len(bits):
            code += bits[i]
            i += 1

            if code in code_to_symbol:
                break

        if code not in code_to_symbol:
            raise ValueError("Invalid or incomplete Huffman code")

        symbol = code_to_symbol[code]

        if symbol != "OTHERS":
            result.append(symbol)
        elif symbol == "OTHERS":
            if bits_needed == 0:
                raise ValueError("Cannot decode OTHERS without VLC bits")

            index_bits = bits[i:i + bits_needed]
            if len(index_bits) != bits_needed:
                raise ValueError("Invalid or incomplete VLC code")

            index = int(index_bits, 2)

            i = i + bits_needed

            result.append(index_to_char[index])


    return "".join(result)
