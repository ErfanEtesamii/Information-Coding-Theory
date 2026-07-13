# فاز ۲: کدگذاری منبع با هافمن + توسعه منبع

import heapq
import itertools
import math


def build_huffman_codes(probs):
    n = len(probs)
    if n == 1:
        return {0: "0"}

    counter = itertools.count()
    heap = []
    for i, p in enumerate(probs):
        heapq.heappush(heap, (p, next(counter), [[i, ""]]))

    while len(heap) > 1:
        p1, _, symbols1 = heapq.heappop(heap)
        p2, _, symbols2 = heapq.heappop(heap)

        for s in symbols1:
            s[1] = "0" + s[1]
        for s in symbols2:
            s[1] = "1" + s[1]

        merged = symbols1 + symbols2
        heapq.heappush(heap, (p1 + p2, next(counter), merged))

    _, _, symbols = heap[0]
    return {i: code for i, code in symbols}


def average_length(probs, codebook):
    return sum(probs[i] * len(codebook[i]) for i in range(len(probs)))


def entropy(probs):
    return -sum(p * math.log2(p) for p in probs if p > 0)


def extend_source(probs, L):
    q = len(probs)
    combos = list(itertools.product(range(q), repeat=L))

    ext_probs = []
    for combo in combos:
        p = 1.0
        for idx in combo:
            p *= probs[idx]
        ext_probs.append(p)

    return combos, ext_probs


def encode_sequence(sequence, L, codebook, combos):
    if len(sequence) % L != 0:
        raise ValueError(f"طول دنباله ({len(sequence)}) باید مضربی از L={L} باشد")

    combo_index = {combo: i for i, combo in enumerate(combos)}
    bits = []

    for start in range(0, len(sequence), L):
        chunk = tuple(int(s) - 1 for s in sequence[start:start + L])
        ext_symbol = combo_index[chunk]
        bits.append(codebook[ext_symbol])

    return "".join(bits)


def decode_bits(bits, codebook, combos):
    reverse = {code: idx for idx, code in codebook.items()}
    decoded = []
    buffer = ""

    for bit in bits:
        buffer += bit
        if buffer in reverse:
            combo = combos[reverse[buffer]]
            decoded.extend(idx + 1 for idx in combo)
            buffer = ""

    return decoded