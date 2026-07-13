# فاز ۱: تعریف منبع و تولید دنباله داده

import numpy as np


def validate_probabilities(probs, tol=1e-6):
    for p in probs:
        if p < 0 or p > 1:
            return False, f"احتمال {p} خارج از بازه [0,1] است"

    total = sum(probs)
    if abs(total - 1) > tol:
        return False, f"مجموع احتمالات برابر {total} است، باید ۱ باشد"

    return True, "ورودی معتبر است"


def generate_sequence(probs, length, seed=None):
    ok, msg = validate_probabilities(probs)
    if not ok:
        raise ValueError(msg)

    rng = np.random.default_rng(seed)
    symbols = np.arange(1, len(probs) + 1)  # S1..Sq
    return rng.choice(symbols, size=length, p=probs)


def sequence_stats(seq, probs):
    n = len(seq)
    unique, counts = np.unique(seq, return_counts=True)

    stats = {}
    for s, c in zip(unique, counts):
        stats[int(s)] = {
            "empirical": c / n,
            "theoretical": probs[s - 1],
        }
    return stats