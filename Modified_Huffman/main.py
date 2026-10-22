import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

from compress import compress
from decompress import decompress


def fix_single_others_vlc_header(compressed_path):
    with compressed_path.open("r+b") as compressed_file:
        compressed_file.readline()
        bits_needed_position = compressed_file.tell()
        bits_needed = compressed_file.readline().strip()
        huffman_count = int(compressed_file.readline())
        huffman_entries = [
            compressed_file.readline()
            for _ in range(huffman_count)
        ]
        vlc_count = int(compressed_file.readline())

        if (
            bits_needed == b"0"
            and vlc_count == 1
            and any(entry.startswith(b"'OTHERS':") for entry in huffman_entries)
        ):
            compressed_file.seek(bits_needed_position)
            compressed_file.write(b"1\n")


def ask_probability_limit():
    while True:
        raw_limit = input("Enter the minimum symbol probability (0 to 1): ").strip()
        try:
            limit = float(raw_limit)
        except ValueError:
            print("Please enter a valid number.")
            continue

        if 0 <= limit <= 1:
            return limit
        print("The probability limit must be between 0 and 1.")


def compress_to_path(text, limit, output_path):
    output_path = output_path.expanduser()
    with tempfile.TemporaryDirectory() as temporary_directory:
        previous_directory = Path.cwd()
        try:
            os.chdir(temporary_directory)
            # The existing compressor prompts for its limit and writes compressed.bin.
            with patch("builtins.input", return_value=str(limit)):
                compress(text)
            fix_single_others_vlc_header(Path("compressed.bin"))
        finally:
            os.chdir(previous_directory)

        generated_file = Path(temporary_directory) / "compressed.bin"
        with generated_file.open("rb") as source:
            with output_path.open("xb") as destination:
                shutil.copyfileobj(source, destination)
    return output_path


def compress_text():
    text = input("Enter the text to compress: ")
    if not text:
        print("Cannot compress empty text.")
        return

    limit = ask_probability_limit()
    raw_output_path = input("Output file [compressed.bin]: ").strip()
    output_path = Path(raw_output_path).expanduser() if raw_output_path else Path("compressed.bin")

    try:
        saved_path = compress_to_path(text, limit, output_path)
    except FileExistsError:
        print(f"Output file already exists; it was not overwritten: {output_path}")
    except (OSError, ValueError, KeyError, IndexError, OverflowError) as error:
        print(f"Compression failed: {error}")
    else:
        print(f"Compression complete. Output saved to: {saved_path.resolve()}")


def compress_text_file():
    input_path = Path(input("Path to the text file: ").strip()).expanduser()
    try:
        text = input_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        print(f"Could not read the input file: {error}")
        return

    if not text:
        print("Cannot compress an empty file.")
        return

    limit = ask_probability_limit()
    raw_output_path = input("Output file [compressed.bin]: ").strip()
    output_path = Path(raw_output_path).expanduser() if raw_output_path else Path("compressed.bin")

    try:
        saved_path = compress_to_path(text, limit, output_path)
    except FileExistsError:
        print(f"Output file already exists; it was not overwritten: {output_path}")
    except (OSError, ValueError, KeyError, IndexError, OverflowError) as error:
        print(f"Compression failed: {error}")
    else:
        print(f"Compression complete. Output saved to: {saved_path.resolve()}")


def decompress_file():
    input_path = Path(input("Path to the compressed file: ").strip()).expanduser()
    output_path = input_path.with_name(f"{input_path.stem}_decompressed.txt")

    try:
        text = decompress(input_path)
        with output_path.open("x", encoding="utf-8") as output_file:
            output_file.write(text)
    except FileExistsError:
        print(f"Output file already exists; it was not overwritten: {output_path}")
    except (OSError, UnicodeError, ValueError, KeyError, IndexError, SyntaxError) as error:
        print(f"Decompression failed: {error}")
    else:
        print(f"Decompression complete. Output saved to: {output_path.resolve()}")


def main():
    print("=" * 40)
    print("   Welcome to Modified Huffman Tool")
    print("   Compression & Decompression")
    print("=" * 40)

    while True:
        print("\n1. Compress text")
        print("2. Compress a text file")
        print("3. Decompress a compressed file")
        print("4. Exit")
        choice = input("Enter your choice: ").strip().lower()

        if choice in {"4", "stop"}:
            print("Goodbye!")
            break
        if choice == "1":
            compress_text()
        elif choice == "2":
            compress_text_file()
        elif choice == "3":
            decompress_file()
        else:
            print("Please choose 1, 2, 3, or 4 (or enter stop).")


if __name__ == "__main__":
    main()
