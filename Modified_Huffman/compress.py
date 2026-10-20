import heapq
from math import ceil, log2

class Node:
    def __init__(self, prob, char):
        self.prob = prob
        self.char = char
        self.left = None
        self.right = None
    def __lt__(self, other): # over riding less than operator pq does know how to compare 2 nodes # this to solve 2 prob are equal
        return self.prob < other.prob

def get_probability(msg , limit):
    freq = {}
    #calc freq of each letter then probability
    for c in msg:
        if c in freq:
            freq[c] += 1
        else :
            freq[c] = 1

    prob = {}
    for p in freq :
        prob[p] = freq[p]/len(msg)

    vlc_codes = {}
    others_count = 0
    new_prob = {}
    new_prob["OTHERS"] = 0

    for char,p in prob.items():
        if  p < limit:
            new_prob["OTHERS"] += p
            vlc_codes[char] = others_count
            others_count += 1
        else :
            new_prob[char] = p

    if new_prob["OTHERS"] == 0 :
        del new_prob["OTHERS"]
        bits_needed = 0
    else :
        bits_needed = ceil(log2(others_count))


    return new_prob , vlc_codes , bits_needed



def assign_huffman_code(node , current_code , table):
    if node.left is None and node.right is None:
        table[node.char] = current_code
        return

    assign_huffman_code(node.left, current_code + "0", table)
    assign_huffman_code(node.right, current_code + "1", table)




def compress(msg = "AAABCCBCBACBCABCAABBCCA"):
    limit = float(input("Enter The Minimum Limit of Symbol Probability: "))
    probabilities , vlc_codes , bits_needed = get_probability(msg , limit)

    pq = []
    for p in probabilities:
        node = Node(probabilities[p], p)
        heapq.heappush(pq,node)
    while len(pq) > 1:
        node1 = heapq.heappop(pq)
        node2 = heapq.heappop(pq)

        new_node = Node(node1.prob + node2.prob, None)
        new_node.left = node1
        new_node.right = node2

        heapq.heappush(pq,new_node)

    root = pq[0]
    table_of_codes = {}
    assign_huffman_code(root , "" , table_of_codes)

    # if msg has only 1 letter
    if len(table_of_codes) == 1:
        char = list(table_of_codes.keys())[0]
        table_of_codes[char] = "0"

    compressed_stream = []
    for char in msg:
        if char in table_of_codes:
            compressed_stream.append(table_of_codes[char])
        else :
            # others group
            compressed_stream.append(table_of_codes["OTHERS"])

            index = vlc_codes[char]
            vlc_binary = f"{index:0{bits_needed}b}"
            compressed_stream.append(vlc_binary)

    compressed_stream = "".join(compressed_stream)


    total_bits = len(compressed_stream)
    # bn3ml padding 34an el binary file read byte by byte
    while len(compressed_stream) % 8 != 0:
        compressed_stream = compressed_stream + "0"

    byte_list = []
    for i in range(0,total_bits,8):
        string_byte = compressed_stream[i:i+8]
        byte_value = int(string_byte, 2)
        byte = byte_value.to_bytes(1, byteorder='big')
        byte_list.append(byte)

    #writing the file -> header is text and compressed stream is binary
    #The header format is:
    # Line 1: total_bits
    # Line 2: bits_needed
    # Line 3: number of entries in Huffman table
    # Next N lines: character:code pairs
    # Next line: number of entries in VLC table
    # Next M lines: character:index pairs
    # Then: the binary compressed data

    with open("compressed.bin", "wb") as f:
        header = f"{total_bits}\n"
        header += f"{bits_needed}\n"
        header += f"{len(table_of_codes)}\n"

        #repr char fixes if the msg has a \n making it '\n'
        for char, code in table_of_codes.items():
            header += f"{repr(char)}:{code}\n"


        header += f"{len(vlc_codes)}\n"
        for char, index in vlc_codes.items():
            header += f"{repr(char)}:{index}\n"


        f.write(header.encode())


        for byte in byte_list:
            f.write(byte)

    print("Compression complete! File saved as compressed.bin")

if __name__ == "__main__":
    compress()