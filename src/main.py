import sys
import source
import huffman
import hamming
import channel
import evaluate

sys.stdout.reconfigure(encoding="utf-8")


def show_menu():
    print("\n--- Huffman/Hamming Simulation over BSC ---")
    print("1) Phase 1 - Source definition and sequence generation")
    print("2) Phase 2 - Huffman coding")
    print("3) Phase 3 - Channel coding (Hamming)")
    print("4) Phase 4 - Channel simulation and decoding")
    print("5) Phase 5 - Evaluation and plotting")
    print("0) Exit")


def run_phase1():
    q = int(input("Number of source symbols (q): "))
    probs_str = input(f"Probability vector, comma-separated ({q} values): ")

    try:
        probs = [float(x.strip()) for x in probs_str.split(",")]
    except ValueError:
        print("Invalid input format, values must be numeric.")
        return

    if len(probs) != q:
        print(f"Number of values entered ({len(probs)}) does not match q={q}.")
        return

    ok, msg = source.validate_probabilities(probs)
    if not ok:
        print("Error:", msg)
        return

    N = int(input("Source sequence length (N): "))
    sequence = source.generate_sequence(probs, N)

    print(f"\nGenerated a sequence of length {N}.")
    print("First 20 symbols:", [int(x) for x in sequence[:20]])

    stats = source.sequence_stats(sequence, probs)
    print("\nEmpirical vs theoretical frequency for each symbol:")
    for symbol, data in sorted(stats.items()):
        print(f"  S{symbol}: empirical={data['empirical']:.4f}  theoretical={data['theoretical']:.4f}")


def run_phase2():
    q = int(input("Number of source symbols (q): "))
    probs_str = input(f"Probability vector, comma-separated ({q} values): ")

    try:
        probs = [float(x.strip()) for x in probs_str.split(",")]
    except ValueError:
        print("Invalid input format, values must be numeric.")
        return

    if len(probs) != q:
        print(f"Number of values entered ({len(probs)}) does not match q={q}.")
        return

    ok, msg = source.validate_probabilities(probs)
    if not ok:
        print("Error:", msg)
        return

    L = int(input("Source extension order (L) [default 1]: ") or "1")
    if L < 1:
        print("L must be at least 1.")
        return

    N = int(input("Source sequence length for testing (N): "))
    if N % L != 0:
        print(f"Error: N={N} must be a multiple of L={L}.")
        return

    sequence = source.generate_sequence(probs, N)
    seq_list = [int(x) for x in sequence]

    combos, ext_probs = huffman.extend_source(probs, L)
    codebook = huffman.build_huffman_codes(ext_probs)

    bits = huffman.encode_sequence(seq_list, L, codebook, combos)
    decoded = huffman.decode_bits(bits, codebook, combos)

    avg_len = huffman.average_length(ext_probs, codebook) / L
    H = huffman.entropy(probs)

    print(f"\nNumber of extended source symbols (q^L): {len(combos)}")
    print(f"Output binary string length: {len(bits)} bits (instead of {N * 8} raw bits)")
    print(f"Average code length per original symbol: {avg_len:.4f} bits")
    print(f"Source entropy: {H:.4f} bits (Shannon lower bound)")
    print("Decoded sequence matches original:", decoded == seq_list)


def run_phase3():
    r = int(input("Number of parity bits (r): "))
    if r < 2:
        print("r must be at least 2.")
        return

    n, k, R = hamming.hamming_params(r)
    print(f"\nn (total block length) = {n}")
    print(f"k (message block length) = {k}")
    print(f"Code rate R = k/n = {R:.4f}")

    H = hamming.build_H(r)
    H_std = hamming.standard_form(H, r, n)
    G = hamming.build_G(H_std, k)

    print(f"\nH matrix (standard form, {n}x{r}):")
    for row in H_std:
        print("  ", row)

    print(f"\nG matrix (standard form, {k}x{n}):")
    for row in G:
        print("  ", row)

    bits_str = input("\nEnter a binary string to test encoding (empty = auto-generate): ").strip()
    if not bits_str:
        bits_str = "".join(str(b) for b in [1, 0, 1, 1, 0, 0, 1, 0, 1, 1])

    encoded, pad = hamming.encode_blocks(bits_str, G, k)
    print(f"\nInput string ({len(bits_str)} bits): {bits_str}")
    print(f"Padding bits added: {pad}")
    print(f"Encoded string ({len(encoded)} bits): {encoded}")


def run_phase4():
    r = int(input("Number of parity bits (r): "))
    if r < 2:
        print("r must be at least 2.")
        return

    n, k, R = hamming.hamming_params(r)
    H = hamming.build_H(r)
    H_std = hamming.standard_form(H, r, n)
    G = hamming.build_G(H_std, k)

    bits_str = input("Binary message string to test (empty = generate random 100-bit): ").strip()
    if not bits_str:
        import random
        bits_str = "".join(random.choice("01") for _ in range(100))

    p_str = input("Channel error probability P (e.g. 0.05): ")
    p_error = float(p_str)
    if not (0 <= p_error < 0.5):
        print("P must be in the range [0, 0.5).")
        return

    # Scenario 1: no channel coding, sequence goes directly through the channel
    received_raw, _ = channel.bsc_transmit(bits_str, p_error)
    errors_raw = sum(1 for a, b in zip(bits_str, received_raw) if a != b)

    # Scenario 2: with Hamming channel coding
    encoded, pad = hamming.encode_blocks(bits_str, G, k)
    received_encoded, _ = channel.bsc_transmit(encoded, p_error)
    channel_errors = sum(1 for a, b in zip(encoded, received_encoded) if a != b)

    decoded_bits, num_corrected, _ = channel.syndrome_decode(received_encoded, H_std, n, r, k)
    decoded_bits = decoded_bits[:len(bits_str)]  # remove padding bits
    errors_remaining = sum(1 for a, b in zip(bits_str, decoded_bits) if a != b)

    print(f"\n--- Scenario 1: no channel protection ---")
    print(f"Corrupted bits out of {len(bits_str)} sent bits: {errors_raw}")

    print(f"\n--- Scenario 2: with Hamming code (n={n}, k={k}, R={R:.4f}) ---")
    print(f"Number of transmitted blocks: {len(encoded) // n}")
    print(f"Bits corrupted by the channel: {channel_errors}")
    print(f"Blocks corrected by the decoder: {num_corrected}")
    print(f"Remaining error bits after correction: {errors_remaining}")


def run_phase5():
    q = int(input("Number of source symbols (q): "))
    probs_str = input(f"Probability vector, comma-separated ({q} values): ")

    try:
        probs = [float(x.strip()) for x in probs_str.split(",")]
    except ValueError:
        print("Invalid input format.")
        return

    if len(probs) != q:
        print(f"Number of values entered ({len(probs)}) does not match q={q}.")
        return

    ok, msg = source.validate_probabilities(probs)
    if not ok:
        print("Error:", msg)
        return

    L = int(input("Source extension order (L) [default 1]: ") or "1")
    r = int(input("Number of Hamming code parity bits (r): "))

    N = int(input("Source sequence length for simulation (N) [suggested: a large number like 5000]: "))
    if N % L != 0:
        print(f"Error: N must be a multiple of L={L}.")
        return

    num_points = int(input("Number of SNR axis points [default 12]: ") or "12")

    n, k, R = hamming.hamming_params(r)
    H = hamming.build_H(r)
    H_std = hamming.standard_form(H, r, n)
    G = hamming.build_G(H_std, k)

    combos, ext_probs = huffman.extend_source(probs, L)
    codebook = huffman.build_huffman_codes(ext_probs)

    sequence = source.generate_sequence(probs, N)
    seq_list = [int(x) for x in sequence]

    huffman_bits = huffman.encode_sequence(seq_list, L, codebook, combos)
    encoded, pad = hamming.encode_blocks(huffman_bits, G, k)

    # p values are spread logarithmically between a small value and near 0.5
    # so both the high-error region and the curve's drop-off are covered
    p_min, p_max = 1e-3, 0.49
    if num_points == 1:
        p_values = [p_max]
    else:
        p_values = [p_min * (p_max / p_min) ** (i / (num_points - 1)) for i in range(num_points)]

    print(f"\nEncoded string length (N''): {len(encoded)} bits")
    print(f"{'p':>10} {'SNR(dB)':>10} {'Pe':>14}")

    pe_values = []
    snr_values = []
    for p in p_values:
        received, _ = channel.bsc_transmit(encoded, p)
        _, _, corrected_full = channel.syndrome_decode(received, H_std, n, r, k)

        pe = evaluate.bit_error_rate(encoded, corrected_full)
        snr = evaluate.snr_db(p)

        pe_values.append(pe)
        snr_values.append(snr)
        print(f"{p:>10.4f} {snr:>10.2f} {pe:>14.6f}")

    p_star = evaluate.shannon_threshold(R)
    snr_star = evaluate.snr_db(p_star)
    print(f"\nCode rate R = {R:.4f}")
    print(f"Shannon threshold: p* = {p_star:.6f}  ->  SNR* = {snr_star:.2f} dB")

    # cap zero-error Pe values so they can be shown on the log scale
    pe_values_for_plot = [max(pe, 1e-6) for pe in pe_values]

    save_path = "ber_curve.png"
    evaluate.plot_results(snr_values, pe_values_for_plot, snr_star, save_path)
    print(f"\nPlot saved to {save_path}.")


def main():
    while True:
        show_menu()
        choice = input("Enter your choice: ")

        if choice == "0":
            break
        elif choice == "1":
            run_phase1()
        elif choice == "2":
            run_phase2()
        elif choice == "3":
            run_phase3()
        elif choice == "4":
            run_phase4()
        elif choice == "5":
            run_phase5()
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()