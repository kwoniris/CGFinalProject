import os
import argparse
from Bio import SeqIO
from bitarray import bitarray
from math import log2, floor

# Mapping nucleotides to binary codes (2 bits for each nucleotide)
nucleotide_to_bits = {
    'A': '00',
    'C': '01',
    'G': '10',
    'T': '11'
}

# Golomb encoding helper function
def golomb_encode(value, m):
    """Encodes a value using Golomb coding with parameter m."""
    q = value // m  # quotient
    r = value % m   # remainder
    # Unary encode the quotient
    unary_code = '1' * q + '0'
    # Binary encode the remainder with optimal length
    b = floor(log2(m))
    k = (1 << b) - m
    if r < k:
        remainder_code = format(r, f'0{b}b')
    else:
        remainder_code = format(r + k, f'0{b + 1}b')
    return unary_code + remainder_code

# Function to find and encode differences as binary with Golomb compression
def compress_sequence_relative_golomb(seq, reference, m):
    """Compresses seq relative to the reference using Golomb encoding for relative positions and binary for substitutions."""
    differences = bitarray()
    last_position = 0  # Track the last SNP position
    differences_str = []  # String representation of differences for intermediate storage

    for i, (ref_nuc, seq_nuc) in enumerate(zip(reference, seq), start=1):
        # Skip if the substitution nucleotide is not in our encoding map (ambiguous base)
        if ref_nuc != seq_nuc and seq_nuc in nucleotide_to_bits:
            # Calculate the relative position from the last SNP
            relative_position = i - last_position
            last_position = i  # Update last SNP position
            
            # Golomb encode the relative position
            pos_diff_bits = golomb_encode(relative_position, m)
            
            # Encode the substitution nucleotide using 2 bits
            substitution_bits = nucleotide_to_bits[seq_nuc]
            
            # Append both the Golomb-encoded position and substitution bits to differences (binary) and to differences_str
            differences.extend(pos_diff_bits)
            differences.extend(substitution_bits)
            differences_str.append(f"{pos_diff_bits}{seq_nuc}")
    
    # Return both bitarray and string format of the differences
    return differences, ''.join(differences_str)

def clear_output_folder(output_folder):
    """Clears the contents of the output folder if it exists."""
    if os.path.exists(output_folder):
        for filename in os.listdir(output_folder):
            file_path = os.path.join(output_folder, filename)
            os.remove(file_path)
        print(f"Cleared existing files in {output_folder}")
    else:
        os.makedirs(output_folder, exist_ok=True)
        print(f"Created new output folder: {output_folder}")

def main(input_folder, reference_file, identifier):
    # Set up and clear output folders based on identifier
    differences_folder = f"compressed_{identifier}_differences"
    binary_string_folder = f"compressed_{identifier}_binary_string"
    binary_bin_folder = f"compressed_{identifier}_binary_bin"
    
    clear_output_folder(differences_folder)
    clear_output_folder(binary_string_folder)
    clear_output_folder(binary_bin_folder)
    
    # Load reference sequence
    reference_record = SeqIO.read(reference_file, "fasta")
    reference_seq = str(reference_record.seq)

    # Golomb parameter for compression
    m = 128

    # Process each file in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".fasta"):
            input_path = os.path.join(input_folder, filename)
            differences_output_path = os.path.join(differences_folder, f"differences_{filename}.txt")
            binary_string_output_path = os.path.join(binary_string_folder, f"compressed_{filename}.txt")
            binary_bin_output_path = os.path.join(binary_bin_folder, f"compressed_{filename}.bin")
            
            # Load the target sequence
            record = SeqIO.read(input_path, "fasta")
            seq = str(record.seq)
            
            # Compress sequence relative to reference using Golomb encoding
            compressed_data, differences_string = compress_sequence_relative_golomb(seq, reference_seq, m)
            
            # Save the differences string to the differences folder
            with open(differences_output_path, "w") as f:
                f.write(differences_string)
            print(f"Saved differences for {filename} to {differences_output_path}")
            
            # Save the differences string to the binary string folder as well
            with open(binary_string_output_path, "w") as f:
                f.write(differences_string)
            print(f"Compressed {filename} and saved binary string to {binary_string_output_path}")
            
            # Save the binary bitarray to a .bin file in the binary bin folder
            with open(binary_bin_output_path, "wb") as f:
                compressed_data.tofile(f)
            print(f"Compressed {filename} and saved binary data to {binary_bin_output_path}")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Compress sequences using Golomb encoding based on a reference sequence.")
    parser.add_argument("--input_folder", type=str, required=True, help="Input folder containing the FASTA files to compress.")
    parser.add_argument("--reference_file", type=str, required=True, help="Reference FASTA file to use for compression.")
    parser.add_argument("--identifier", type=str, required=True, help="Identifier to use in the output folder name (e.g., 'mtdna').")

    args = parser.parse_args()
    
    # Run main compression function
    main(args.input_folder, args.reference_file, args.identifier)
