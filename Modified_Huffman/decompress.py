import ast 

def decompress(filename, padding_bits):
    with open("compressed.bin", "rb") as f:
        total_bits = int(f.readline())
        bits_needed = int(f.readline())


        huffman_count = int(f.readline())
        huffman_table = {}
        for _ in range(huffman_count):
            char, code = f.readline().decode().rstrip("\n").split(":")
            char = ast.literal_eval(char)
            huffman_table[char] = code


        vlc_count = int(f.readline())
        vlc_table = {}
        for _ in range(vlc_count):
            char, index = f.readline().decode().rstrip("\n").split(":")
            char = ast.literal_eval(char)
            vlc_table[char] = int(index)


        compressed_data = f.read()


        bits = ""
        for byte in compressed_data:
            bits += f"{byte:08b}"

        bits = bits[:total_bits]

        result = []
        while bits:
            if bits[0] == "0":
                result.append("A")
                bits = bits[1:]
            else:
                result.append(huffman_table[bits[:2]])
                bits = bits[2:]

        return "".join(result)
