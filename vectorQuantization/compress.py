import os
import math
import numpy as np
from PIL import Image
from decompress import decompress


def assign_vectors(X, codebook):
    labels = []
    for vector in X :
        min_dist = float("inf")
        best_index = 0

        for i in range (len(codebook)):
            distance = calculate_distance(vector , codebook[i])
            if distance < min_dist :
                min_dist = distance
                best_index = i
        labels.append(best_index)

    return np.array(labels)
    

def calculate_distance(vector1, vector2):
    distance = 0

    for i in range(len(vector1)):
        distance += abs(vector1[i] - vector2[i])

    return distance

def refine_codebook(X, codebook):
    while True:
        labels = assign_vectors(X, codebook)

        new_codebook = []

        for i in range(len(codebook)):
            cluster = X[labels == i]

            if len(cluster) == 0:
                new_codebook.append(codebook[i])
            else:
                new_centroid = np.mean(cluster, axis=0)
                new_codebook.append(new_centroid)

        new_codebook = np.array(new_codebook)

        if np.allclose(codebook, new_codebook):
            break

        codebook = new_codebook

    return codebook



def build_codebook(X, K):

    if K < 1:
        raise ValueError("K must be at least 1.")

    if K & (K - 1) != 0:
        raise ValueError("K must be a power of 2.")

    if K > len(X):
        raise ValueError(
            "K cannot be greater than the number of image blocks."
        )

    codebook = np.array([np.mean(X, axis=0)])

    while len(codebook) < K:

        new_codebook = []

        for centroid in codebook:
            centroid1 = np.round(centroid - 0.5)
            centroid2 = np.round(centroid + 0.5)

            new_codebook.append(centroid1)
            new_codebook.append(centroid2)

        codebook = np.array(new_codebook)

        
        codebook = refine_codebook(X, codebook)

    return codebook


def compress(
    image_path,
    bh,
    bw,
    K,
    codebook_path,
    compressed_path
):

    if bh < 1 or bw < 1:
        raise ValueError("Block dimensions must be positive.")

    if K < 1:
        raise ValueError("K must be at least 1.")

    if K & (K - 1) != 0:
        raise ValueError("K must be a power of 2.")

    image = Image.open(image_path).convert("L")
    image = np.array(image, dtype=np.uint8)
    H, W = image.shape

    pad_h = (bh - H % bh) % bh
    pad_w = (bw - W % bw) % bw

    padded_image = np.pad(
        image,
        ((0, pad_h), (0, pad_w)),
        mode="edge"
    )

    padded_h, padded_w = padded_image.shape



    blocks = []
    for i in range(0, padded_h, bh):
        for j in range(0, padded_w, bw):

            block = padded_image[i:i+bh, j:j+bw]

            blocks.append(block.flatten())

    X = np.array(blocks, dtype=np.float64)

    n_blocks = len(X)

    if K > n_blocks:
        raise ValueError(
            f"K ({K}) cannot exceed number of blocks ({n_blocks})."
        )

    print("\nBuilding codebook using LBG...")

    codebook = build_codebook(X, K)

    codebook = np.clip(
        np.rint(codebook),
        0,
        255
    ).astype(np.uint8)

    labels = assign_vectors(
        X,
        codebook.astype(np.float64)
    )


    codebook = codebook.reshape(K, bh, bw)

    with open(codebook_path, "wb") as f:
        np.savez(
            f,
            codebook=codebook,
            orig_h=H,
            orig_w=W,
            bh=bh,
            bw=bw
        )


    b = max(1, math.ceil(math.log2(K)))

    bits = (
        (labels[:, None] >> np.arange(b - 1, -1, -1))
        & 1
    ).astype(np.uint8).ravel()

    packed_bits = np.packbits(bits, bitorder="big")

    with open(compressed_path, "wb") as f:
        f.write(packed_bits.tobytes())


    original_size = H * W

    codebook_size = os.path.getsize(codebook_path)
    compressed_size = os.path.getsize(compressed_path)

    total_compressed_size = codebook_size + compressed_size

    compression_ratio = (
        original_size / total_compressed_size
        if total_compressed_size > 0
        else 0
    )

    print("\nCompression results:")
    print(f"Original image size: {original_size} bytes")
    print(f"Number of blocks: {n_blocks}")
    print(f"Codebook size: {codebook_size} bytes")
    print(f"Compressed stream size: {compressed_size} bytes")
    print(f"Total compressed size: {total_compressed_size} bytes")
    print(f"Compression ratio: {compression_ratio:.4f}:1")
    print("")

    return compression_ratio

