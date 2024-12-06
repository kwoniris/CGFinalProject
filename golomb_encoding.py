import os
import argparse
from Bio import SeqIO
from bitarray import bitarray
from math import log2, ceil

# Mapping nucleotides to binary codes
nucleotide_to_bits = {
    'A': '00',
    'C': '01',
    'G': '10',
    'T': '11'
}

# Golomb encoding function
def golomb_encode(value, m):
    """Encodes a value using Golomb coding with parameter m."""
    q = value // m  # quotient
    r = value % m   # remainder
    unary_code = '1' * q + '0'  # Unary encode the quotient
    b = ceil(log2(m))
    k = (1 << b) - m
    if r < k:
        remainder_code = format(r, f'0{b}b')
    else:
        remainder_code = format(r + k, f'0{b + 1}b')
    return unary_code + remainder_code

def compress_sequence(seq, reference, m):
    """Compresses seq relative to the reference using Golomb encoding for differences."""
    differences_bitarray = bitarray()
    differences_str = []  # Collects the binary string representation

    last_position = 0
    for i, (ref_nuc, seq_nuc) in enumerate(zip(reference, seq), start=1):
        if ref_nuc != seq_nuc and seq_nuc in nucleotide_to_bits:
            relative_position = i - last_position
            last_position = i

            # Golomb encode position and add substitution binary
            pos_bits = golomb_encode(relative_position, m)
            sub_bits = nucleotide_to_bits[seq_nuc]

            # Append to bitarray and binary string list
            differences_bitarray.extend(pos_bits + sub_bits)
            differences_str.append(pos_bits + sub_bits)

    return differences_bitarray, differences_str  # Return both bitarray and list of differences

def main(input_folder, reference_file, identifier, m):
    # Ensure output folders exist
    os.makedirs(f"golomb_{identifier}_binary_string", exist_ok=True)
    os.makedirs(f"golomb_{identifier}_binary_bin", exist_ok=True)
    os.makedirs(f"golomb_{identifier}_differences", exist_ok=True)

    # Load reference sequence
    reference_record = SeqIO.read(reference_file, "fasta")
    reference_seq = str(reference_record.seq)

    for filename in os.listdir(input_folder):
        if filename.endswith(".fasta"):
            input_path = os.path.join(input_folder, filename)
            record = SeqIO.read(input_path, "fasta")
            seq = str(record.seq)

            # Compress sequence relative to reference
            bitarray_data, differences_str = compress_sequence(seq, reference_seq, m)

            # Save the binary string representation
            string_output_path = os.path.join(f"golomb_{identifier}_binary_string", f"compressed_{filename}.txt")
            with open(string_output_path, "w") as f:
                f.write(''.join(differences_str))
            print(f"Saved binary string to {string_output_path}")

            # Save the binary bitarray data to a .bin file
            binary_output_path = os.path.join(f"golomb_{identifier}_binary_bin", f"compressed_{filename}.bin")
            with open(binary_output_path, "wb") as f:
                bitarray_data.tofile(f)
            print(f"Saved binary data to {binary_output_path}")

            # Save differences string for readability/debugging
            differences_output_path = os.path.join(f"golomb_{identifier}_differences", f"differences_{filename}.txt")
            with open(differences_output_path, "w") as f:
                f.write('\n'.join(differences_str))
            print(f"Saved differences string to {differences_output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compress sequences using Golomb encoding based on a reference sequence.")
    parser.add_argument("--input_folder", type=str, required=True, help="Folder containing the FASTA files to compress.")
    parser.add_argument("--reference_file", type=str, required=True, help="Reference FASTA file for compression.")
    parser.add_argument("--identifier", type=str, required=True, help="Identifier for naming output folders.")
    parser.add_argument("--m", type=int, required=True, help="Golomb encoding parameter m.")

    args = parser.parse_args()
    main(args.input_folder, args.reference_file, args.identifier, args.m)
