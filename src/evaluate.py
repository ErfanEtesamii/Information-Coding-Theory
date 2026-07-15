# Phase 5: Pe calculation, SNR conversion, Shannon capacity limit and plotting

import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def bit_error_rate(sent_bits, received_bits):
    n = len(sent_bits)
    errors = sum(1 for a, b in zip(sent_bits, received_bits) if a != b)
    return errors / n


def snr_db(p):
    # SNR = (1-p)/p as defined in the project document, converted to dB
    ratio = (1 - p) / p
    return 10 * math.log10(ratio)


def channel_capacity(p):
    # BSC channel capacity: C(p) = 1 - H_b(p)
    if p <= 0:
        return 1.0
    if p >= 1:
        return 0.0
    return 1 + p * math.log2(p) + (1 - p) * math.log2(1 - p)


def shannon_threshold(R):
    # Binary search for p* such that C(p*) = R.
    # C(p) is monotonically decreasing over (0, 0.5], so binary search is valid.
    lo, hi = 1e-9, 0.5 - 1e-9
    for _ in range(200):
        mid = (lo + hi) / 2
        if channel_capacity(mid) > R:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def plot_results(snr_values, pe_values, shannon_snr, save_path):
    plt.figure(figsize=(8, 6))
    plt.semilogy(snr_values, pe_values, marker="o", label="Hamming Code (Simulation)")
    plt.axvline(x=shannon_snr, color="red", linestyle="--", label="Shannon Limit")
    plt.xlabel("SNR (dB)")
    plt.ylabel("Pe (Bit Error Rate)")
    plt.title("BER vs SNR over BSC")
    plt.grid(True, which="both", linestyle=":")
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()