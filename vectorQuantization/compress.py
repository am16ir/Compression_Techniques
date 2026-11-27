
import os
import math
import numpy as np
from PIL import Image


# ==========================================
# 1. Assign each vector to nearest codeword
# ==========================================

def assign_vectors(X, codebook, batch_size=8192):
    labels = np.empty(len(X), dtype=np.int32)
    errors = np.empty(len(X), dtype=np.float64)

    codebook_norms = np.sum(codebook ** 2, axis=1)

    for start in range(0, len(X), batch_size):
        end = min(start + batch_size, len(X))
        batch = X[start:end]

        distances = (
            np.sum(batch ** 2, axis=1, keepdims=True)
            + codebook_norms[None, :]
            - 2 * batch @ codebook.T
        )

        np.maximum(distances, 0, out=distances)

        batch_labels = np.argmin(distances, axis=1)

        labels[start:end] = batch_labels
        errors[start:end] = distances[
            np.arange(len(batch)), batch_labels
        ]

    return labels, errors


# ==========================================
# 2. Refine codebook using LBG
# ==========================================

def refine_codebook(X, codebook, max_iter=100, tolerance=0.001):

    codebook = codebook.copy()

    for _ in range(max_iter):

        labels, errors = assign_vectors(X, codebook)

        new_codebook = codebook.copy()

        for i in range(len(codebook)):

            cluster = X[labels == i]

            if len(cluster) > 0:
                new_codebook[i] = np.mean(cluster, axis=0)

        # Handle empty clusters
        empty_clusters = np.where(
            np.bincount(labels, minlength=len(codebook)) == 0
        )[0]

        if len(empty_clusters) > 0:

            worst_indices = np.argsort(errors)[::-1]
            used_indices = set()

            for cluster_index in empty_clusters:

                for sample_index in worst_indices:
                    if int(sample_index) not in used_indices:
                        new_codebook[cluster_index] = X[sample_index]
                        used_indices.add(int(sample_index))
                        break

        difference = np.max(np.abs(new_codebook - codebook))

        codebook = new_codebook

        if difference < tolerance:
            break

    return codebook


# ==========================================
# 3. Build Codebook using LBG algorithm
# ==========================================

def build_codebook(X, K, epsilon=0.01):

    if K < 1:
        raise ValueError("K must be at least 1.")

    if K > len(X):
        raise ValueError(
            "K cannot be greater than the number of image blocks."
        )

    # Start with one centroid: the mean of all vectors
    codebook = np.mean(X, axis=0, keepdims=True)

    # Small perturbation for splitting
    delta = epsilon * np.std(X, axis=0)
    delta = np.maximum(delta, epsilon)

    # Split until we reach K codewords
    while len(codebook) < K:

        labels, errors = assign_vectors(X, codebook)

        # Calculate distortion for each cluster
        distortions = np.bincount(
            labels,
            weights=errors,
            minlength=len(codebook)
        )

        # Select the cluster with highest distortion
        split_index = np.argmax(distortions)

        old_centroid = codebook[split_index]

        # Split centroid into two
        centroid_1 = old_centroid + delta
        centroid_2 = old_centroid - delta

        # Replace selected centroid and add the second one
        codebook[split_index] = centroid_1

        codebook = np.vstack([
            codebook,
            centroid_2
        ])

        # Refine the codebook
        codebook = refine_codebook(X, codebook)

    return codebook


# ==========================================
# 4. Compression
# ==========================================

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

    # Extract blocks in row-major order
    blocks = (
        padded_image
        .reshape(padded_h // bh, bh, padded_w // bw, bw)
        .transpose(0, 2, 1, 3)
        .reshape(-1, bh * bw)
    )

    # Convert blocks to float for calculations
    X = blocks.astype(np.float64)

    n_blocks = len(X)

    if K > n_blocks:
        raise ValueError(
            f"K ({K}) cannot exceed number of blocks ({n_blocks})."
        )

    print("\nBuilding codebook using LBG...")

    # Build codebook
    codebook = build_codebook(X, K)

    # Convert codebook to uint8
    codebook = np.clip(
        np.rint(codebook),
        0,
        255
    ).astype(np.uint8)

    # Assign blocks using the final uint8 codebook
    labels, _ = assign_vectors(
        X,
        codebook.astype(np.float64)
    )

    # ======================================
    # Save codebook
    # ======================================

    codebook = codebook.reshape(K, bh, bw)

    with open(codebook_path, "wb") as f:
        np.savez(
            f,
            codebook=codebook,
            orig_h=H,
            orig_w=W
        )

    # ======================================
    # Pack labels into binary stream
    # MSB first, last byte zero-padded
    # ======================================

    b = max(1, math.ceil(math.log2(K)))

    bits = (
        (labels[:, None] >> np.arange(b - 1, -1, -1))
        & 1
    ).astype(np.uint8).ravel()

    packed_bits = np.packbits(bits, bitorder="big")

    with open(compressed_path, "wb") as f:
        f.write(packed_bits.tobytes())

    # ======================================
    # Calculate compression ratio
    # ======================================

    original_size = H * W

    codebook_size = os.path.getsize(codebook_path)
    compressed_size = os.path.getsize(compressed_path)

    total_compressed_size = codebook_size + compressed_size

    compression_ratio = (
        original_size / total_compressed_size
        if total_compressed_size > 0
        else 0
    )

    print("\n========== Compression Results ==========")
    print(f"Original image size: {original_size} bytes")
    print(f"Number of blocks: {n_blocks}")
    print(f"Codebook size: {codebook_size} bytes")
    print(f"Compressed stream size: {compressed_size} bytes")
    print(f"Total compressed size: {total_compressed_size} bytes")
    print(f"Compression ratio: {compression_ratio:.4f}:1")
    print("=========================================")

    return compression_ratio

