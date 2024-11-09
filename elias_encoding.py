import os
import argparse
from Bio import SeqIO
from bitarray import bitarray
from math import log2

# Mapping nucleotides to binary codes
nucleotide_to_bits = {
    'A': '00',
    'C': '01',
    'G': '10',
    'T': '11'
}

def binary(x, l=1):
    """Formats integer x as a binary string of length l."""
    return format(x, f'0{l}b')

def unary(x):
    """Unary encoding of integer x."""
    return '1' * x + '0'

def elias_generic(lencoding, x):
    """Generalized Elias encoding with specified length encoding."""
    if x == 0:
        return '0'
    l = 1 + int(log2(x))
    a = x - (1 << (l - 1))
    k = l - 1
    return lencoding(l) + binary(a, k)

def elias_gamma(x):
    """Elias Gamma encoding of integer x."""
    return elias_generic(unary, x)

def elias_delta(x):
    """Elias Delta encoding of integer x."""
    return elias_generic(elias_gamma, x)

def compress_sequence(seq, reference, encoding_type):
    """Compresses seq relative to the reference using specified Elias encoding."""
    differences_bitarray = bitarray()
    differences_str = []

    last_position = 0
    for i, (ref_nuc, seq_nuc) in enumerate(zip(reference, seq), start=1):
        if ref_nuc != seq_nuc and seq_nuc in nucleotide_to_bits:
            relative_position = i - last_position
            last_position = i
            
            # Encode position with chosen encoding
            if encoding_type == 'gamma':
                pos_bits = elias_gamma(relative_position)
            elif encoding_type == 'delta':
                pos_bits = elias_delta(relative_position)
            elif encoding_type == 'all':  # Generate both
                pos_bits_gamma = elias_gamma(relative_position)
                pos_bits_delta = elias_delta(relative_position)
                sub_bits = nucleotide_to_bits[seq_nuc]
                
                # Return both encodings in separate dictionaries
                return {
                    "gamma": (pos_bits_gamma, sub_bits),
                    "delta": (pos_bits_delta, sub_bits)
                }

            sub_bits = nucleotide_to_bits[seq_nuc]
            differences_bitarray.extend(pos_bits + sub_bits)
            differences_str.append(pos_bits + sub_bits)

    return differences_bitarray, differences_str

def main(input_folder, reference_file, identifier, encoding_type):
    # Ensure output folders exist for selected encoding(s)
    if encoding_type in ['gamma', 'all']:
        os.makedirs(f"elias_gamma_{identifier}_binary_string", exist_ok=True)
        os.makedirs(f"elias_gamma_{identifier}_binary_bin", exist_ok=True)
    if encoding_type in ['delta', 'all']:
        os.makedirs(f"elias_delta_{identifier}_binary_string", exist_ok=True)
        os.makedirs(f"elias_delta_{identifier}_binary_bin", exist_ok=True)

    # Load reference sequence
    reference_record = SeqIO.read(reference_file, "fasta")
    reference_seq = str(reference_record.seq)

    for filename in os.listdir(input_folder):
        if filename.endswith(".fasta"):
            input_path = os.path.join(input_folder, filename)
            record = SeqIO.read(input_path, "fasta")
            seq = str(record.seq)

            if encoding_type == 'all':
                # Run both encodings
                gamma_result = compress_sequence(seq, reference_seq, 'gamma')
                delta_result = compress_sequence(seq, reference_seq, 'delta')

                # Save Elias Gamma results
                save_results(gamma_result, f"elias_gamma_{identifier}", filename)
                # Save Elias Delta results
                save_results(delta_result, f"elias_delta_{identifier}", filename)
                
            else:
                # Run single encoding
                result = compress_sequence(seq, reference_seq, encoding_type)
                save_results(result, f"elias_{encoding_type}_{identifier}", filename)

def save_results(result, folder_prefix, filename):
    """Helper function to save compressed results to files."""
    bitarray_data, differences_str = result

    # Save binary string representation
    string_output_path = os.path.join(f"{folder_prefix}_binary_string", f"compressed_{filename}.txt")
    with open(string_output_path, "w") as f:
        f.write(''.join(differences_str))
    print(f"Saved binary string to {string_output_path}")

    # Save binary bitarray data to a .bin file
    binary_output_path = os.path.join(f"{folder_prefix}_binary_bin", f"compressed_{filename}.bin")
    with open(binary_output_path, "wb") as f:
        bitarray_data.tofile(f)
    print(f"Saved binary data to {binary_output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compress sequences using Elias Gamma, Delta, or both encodings based on a reference sequence.")
    parser.add_argument("--input_folder", type=str, required=True, help="Folder containing the FASTA files to compress.")
    parser.add_argument("--reference_file", type=str, required=True, help="Reference FASTA file for compression.")
    parser.add_argument("--identifier", type=str, required=True, help="Identifier for naming output folders.")
    parser.add_argument("--encoding", type=str, choices=['gamma', 'delta', 'all'], default='all',
                        help="Specify encoding type: 'gamma', 'delta', or 'all' (default).")

    args = parser.parse_args()
    main(args.input_folder, args.reference_file, args.identifier, args.encoding)
