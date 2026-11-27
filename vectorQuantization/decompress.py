import sys
import math
import numpy as np
from PIL import Image


def decompress(codebook_path, compressed_path, out_path):
    data = np.load(codebook_path)
    cb = data["codebook"]
    H = int(data["orig_h"])
    W = int(data["orig_w"])
    K, bh, bw = cb.shape

    b = max(1, int(np.ceil(np.log2(K))))
    rows = math.ceil(H / bh)
    cols = math.ceil(W / bw)
    n_blocks = rows * cols

    bits = np.unpackbits(np.fromfile(compressed_path, dtype=np.uint8))
    bits = bits[: n_blocks * b].reshape(n_blocks, b)

    labels = []
    for i in range(n_blocks):
        label = 0
        for j in range(b):
            label = label * 2 + int(bits[i][j])
        labels.append(label)

    blocks = []
    for label in labels:
        blocks.append(cb[label])
    blocks = np.array(blocks)

    img = blocks.reshape(rows, cols, bh, bw)
    img = img.transpose(0, 2, 1, 3).reshape(rows * bh, cols * bw)

    img = img[:H, :W]
    Image.fromarray(img.astype(np.uint8)).save(out_path)


if __name__ == "__main__":
    decompress(sys.argv[1], sys.argv[2], sys.argv[3])
