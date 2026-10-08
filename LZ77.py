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

def process_text(text, search_window, lookahead_window , flag):
    compression_tags = compress_lz77(text, search_window, lookahead_window)
    decompressed = decompress_lz77(compression_tags)
    if text == decompressed:
        print("Text compressed successfully")
        
        text_size = get_text_size(text)
        compressed_size = get_tags_size(compression_tags)
        compression_ratio = round(compressed_size / text_size, 3)
        
        print(f"Size before: {text_size} bits.")
        print(f"Size after: {compressed_size} bits.")
        print(f"Compression ratio: {compression_ratio}")
        if flag :
            print(f"Compressed Tags: ")
            for tag in compression_tags :
                print(tag)

    else:
        print("A problem occurred and the decompressed text don't match the original text")

def main() :
    search_window = 12
    lookahead_window = 11
    while True:
        print("#" * 30)
        print("Application Menu")
        print(f"Current search window length: {search_window}")
        print(f"Current lookahead window length: {lookahead_window}")
        print("1- Enter text.")
        print("2- Change search window length.")
        print("3- Change lookahed window length.")
        print("0- Exit.")
        print("#" * 30)
        choice = int(input())
        match choice:
            case 1:
                text = input("Enter your text: ")
                chr = input("Do you want to display compressed tags? y/n\n")
                flag = (chr == "y")
                process_text(text, search_window, lookahead_window , flag)

            case 2:
                new_length = int(input("Enter the new length: "))
                if new_length > 0 :
                    search_window = new_length
                    print("Search window updated successfully")
                else:
                    print("Invalid length")
            case 3:
                new_length = int(input("Enter the new length: "))
                if new_length > 0 :
                    lookahead_window = new_length
                    print("Lookahead window updated successfully")
                else:
                    print("Invalid length")
            case 0:
                exit(0)
            case _:
                print("Invalid choice.")

if __name__ == "__main__":
    main()

    