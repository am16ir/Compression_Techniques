#==========================================
# 5. Interactive Main
# ==========================================

import os
import compress
import numpy as np

if __name__ == "__main__":

    print("======================================")
    print("       VECTOR QUANTIZATION - LBG")
    print("======================================")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    try:
        print("\n1. Compress")
        print("2. Decompress")
        choice = input("Choose an option: ").strip()

        if choice == "2":
            print("\nDecompression is not implemented yet.")
        elif choice != "1":
            raise ValueError("Please choose 1 or 2.")
        else:
            image_path = input(
                "\nEnter image name or full path: "
            ).strip().strip('"')

            # If only a filename is entered,
            # search relative to the script directory
            if not os.path.isabs(image_path):
                image_path = os.path.join(BASE_DIR, image_path)

            bh = int(input("Enter block height: "))
            bw = int(input("Enter block width: "))
            K = int(input("Enter codebook size (K): "))

            # Create output directory
            OUTPUT_DIR = os.path.join(BASE_DIR, "output")
            os.makedirs(OUTPUT_DIR, exist_ok=True)

            codebook_path = os.path.join(
                OUTPUT_DIR,
                "codebook.npz"
            )

            compressed_path = os.path.join(
                OUTPUT_DIR,
                "compressed.bin"
            )

            # Run compression
            ratio = compress.compress(
                image_path,
                bh,
                bw,
                K,
                codebook_path,
                compressed_path
            )

            print("\nCompression completed successfully!")
            print(f"Output folder: {OUTPUT_DIR}")

    except (ValueError, FileNotFoundError, OSError) as e:

        print("\nError:", e)
