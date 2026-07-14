# فاز ۳: کد همینگ (r,2) - ساخت H و G و کدگذاری کانال


def hamming_params(r):
    n = 2 ** r - 1
    k = n - r
    R = k / n
    return n, k, R


def build_H(r):
    n = 2 ** r - 1
    H = []
    for i in range(1, n + 1):
        bits = [(i >> (r - 1 - b)) & 1 for b in range(r)]
        H.append(bits)
    return H


def standard_form(H, r, n):
    # سطرهایی که وزن همینگشون ۱ است (یعنی نمایش باینری یک توان دو هستند) رو
    # فقط با جابه‌جایی سطری به انتهای ماتریس منتقل می‌کنیم تا r سطر آخر
    # دقیقا ماتریس همانی I_r بشه. هیچ ستونی جابه‌جا نمیشه.
    power_rows = []
    other_rows = []

    for row in H:
        if sum(row) == 1:
            power_rows.append(row)
        else:
            other_rows.append(row)

    power_rows.sort(key=lambda row: row.index(1))

    return other_rows + power_rows


def build_G(H_standard, k):
    A_T = H_standard[:k]
    G = []
    for i in range(k):
        identity_part = [1 if j == i else 0 for j in range(k)]
        G.append(identity_part + A_T[i])
    return G


def _mat_vec_mult_gf2(message, G):
    k = len(G)
    n = len(G[0])
    result = [0] * n
    for i in range(k):
        if message[i] == 1:
            for j in range(n):
                result[j] ^= G[i][j]
    return result


def encode_blocks(bits, G, k):
    pad = (-len(bits)) % k
    padded_bits = bits + "0" * pad

    encoded_blocks = []
    for start in range(0, len(padded_bits), k):
        message = [int(b) for b in padded_bits[start:start + k]]
        codeword = _mat_vec_mult_gf2(message, G)
        encoded_blocks.append("".join(str(b) for b in codeword))

    return "".join(encoded_blocks), pad