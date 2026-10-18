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

    for c in msg:
        if c in freq:
            freq[c] += 1
        else :
            freq[c] = 1

    prob = {}
    for p in freq :
        prob[p] = freq[p]/len(msg)

    new_prob = {}
    new_prob["OTHERS"] = 0
    for char,p in prob.items():
        if  p < limit:
            new_prob["OTHERS"] += p
        else :
            new_prob[char] = p

    if new_prob["OTHERS"] == 0 :
        del new_prob["OTHERS"]

    return new_prob



def assign_huffman_code(node , current_code , table):
    if node.left is None and node.right is None:
        table[node.char] = current_code
        return

    assign_huffman_code(node.left, current_code + "0", table)
    assign_huffman_code(node.right, current_code + "1", table)




def compress(msg):
    limit = float(input("Enter The Minimum Limit of Symbol Probability: "))
    probabilities = get_probability(msg , limit)

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

    compressed_stream = []
    # i forget the others group we must send the vlc code first
    for char in msg:
        compressed_stream.append(table_of_codes[char])

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

    print("The compressed stream is:",compressed_stream)
