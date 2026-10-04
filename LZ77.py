from dataclasses import dataclass
import math
@dataclass
class Tag :
    pos : int
    length : int
    next_symbol : str


def compress_lz77(word, search_window = 12, lookahead_window = 11) :
    tags = []
    i = 0

    while i < len(word):
        
        j = i -1
        longest_len = 0 
        longest_pos = 0

        while (i - j <= search_window) and (j >= 0):
            

            if word[j] == word[i]:
                cnt = 1

                while (cnt < lookahead_window) and (cnt + i < len(word)) and (cnt + j < len(word)):
                    if word[j + cnt] == word[cnt + i] :
                        cnt+=1
                    else :
                        break
                            

                if (cnt > longest_len):
                    longest_len = cnt
                    longest_pos = i - j

            j-=1

        if longest_len > 0:
            if i + longest_len < len(word):
                nxt_sym = word[i + longest_len]
            else :
                nxt_sym = ""  

            tags.append(Tag(longest_pos , longest_len , nxt_sym))
            i+=longest_len + 1
        else :
            tags.append(Tag(0 , 0 , word[i]))
            i+=1
        
    return tags

def decompress_lz77(tags) :
    original = []
    i = 0
    for tag in tags :
        pos = tag.pos
        length = tag.length
        nxt_sym = tag.next_symbol

        if pos > 0 :
            j = i - pos

            for k in range (length):
                original.append(original[j + k])
            i+=length

        original.append(nxt_sym)
        i+=1

    return "".join(original)    

def get_tags_size(tags):
    max_pos = 1
    max_length = 1
    
    for tag in tags:
        
        if tag.pos > max_pos:
            max_pos = tag.pos
        
        if tag.length > max_length:
            max_length = tag.length
            
    pos_bits = math.ceil(math.log2(max_pos + 1))
    length_bits = math.ceil(math.log2(max_length + 1))
    
    return (pos_bits + length_bits + 8) * len(tags)
    
def get_text_size(text):
    return len(text) * 8

def main() :
    s = input("Enter a string to compress using LZ77:")
    #s = "ABAABABAABBBBBBBBBBBBA"

    compress_tags = compress_lz77(s, 15, 15)
    for c in compress_tags:
        print(c)

    decompressed_string = decompress_lz77(compress_tags)
    print(decompressed_string)

    if decompressed_string == s:
        print("Compressed & decompressed successfully")
        original_size = get_text_size(s)
        compressed_size = get_tags_size(compress_tags)
        print(f"Compression Ratio: {round(compressed_size / original_size, 3)}")

if __name__ == "__main__":
    main()