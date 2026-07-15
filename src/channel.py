# فاز ۴: شبیه‌سازی کانال BSC و کدگشایی سندروم

import numpy as np


def bsc_transmit(bits, p_error, seed=None):
    rng = np.random.default_rng(seed)
    flips = rng.random(len(bits)) < p_error

    received = []
    for bit_char, flip in zip(bits, flips):
        bit = int(bit_char)
        if flip:
            bit ^= 1
        received.append(str(bit))

    return "".join(received), flips


def _build_syndrome_table(H_std):
    return {tuple(row): i for i, row in enumerate(H_std)}


def _compute_syndrome(block, H_std, r):
    s = [0] * r
    for bit, h_row in zip(block, H_std):
        if bit == 1:
            for j in range(r):
                s[j] ^= h_row[j]
    return s


def syndrome_decode(received_bits, H_std, n, r, k):
    syndrome_table = _build_syndrome_table(H_std)
    zero_syndrome = tuple([0] * r)

    message_bits = []
    num_corrected = 0

    for start in range(0, len(received_bits), n):
        block = [int(b) for b in received_bits[start:start + n]]
        s = tuple(_compute_syndrome(block, H_std, r))

        if s != zero_syndrome and s in syndrome_table:
            error_pos = syndrome_table[s]
            block[error_pos] ^= 1
            num_corrected += 1

        message_bits.extend(block[:k])

    return "".join(str(b) for b in message_bits), num_corrected