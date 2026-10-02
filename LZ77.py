from dataclasses import dataclass

@dataclass
class Tag :
    length : int
    pos : int
    next_symbol : str



def LZ77_compression(word) :
    search_window = 12
    look_ahead = 11
    tags = []
    i = 0

    while i < len(word):
        
        j = i -1
        longest_len = 0 
        longest_pos = 0

        while (i - j <= search_window) and (j >= 0):
            

            if word[j] == word[i]:
                cnt = 1

                while (cnt < look_ahead) and (cnt + i < len(word)) and (cnt + j < len(word)):
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
                nxt_sym = ""  
            nxt_sym = word[i + longest_len]

            tags.append(Tag(longest_pos , longest_len , nxt_sym))
            i+=longest_len + 1
        else :
            tags.append(Tag(0 , 0 , word[i]))
            i+=1
        
    return tags


def decompression() :
    return 


def main() :
    #s = input("Enter a string to compress using LZ77:")
    s = "ABAABABAABBBBBBBBBBBBA"
    # ABAABABAABBBBBBBBBBBBA
    compress = LZ77_compression(s)
    for c in compress:
        print(c)


if __name__ == "__main__":
    main()