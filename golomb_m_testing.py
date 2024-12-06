import os
import argparse
import matplotlib.pyplot as plt
from golomb_encoding import compress_sequence  # Assuming your code is in golomb_encoding.py
from Bio import SeqIO

def test_compression(input_folder, reference_file, temp_output_folder):
    """Tests different values of m for compression and calculates compression ratio."""
    # Load reference sequence
    reference_record = SeqIO.read(reference_file, "fasta")
    reference_seq = str(reference_record.seq)

    m_values = range(2, 40)  # m values from 2 to 256
    compression_ratios = []

    # Ensure temporary output folder exists
    os.makedirs(temp_output_folder, exist_ok=True)

    for m in m_values:
        total_original_size = 0
        total_compressed_size = 0

        for filename in os.listdir(input_folder):
            if filename.endswith(".fasta"):
                input_path = os.path.join(input_folder, filename)

                # Get the original size of the file in bits
                original_size = os.path.getsize(input_path)  # Convert bytes to bits

                record = SeqIO.read(input_path, "fasta")
                seq = str(record.seq)

                # Compress sequence and store bitarray in a temporary file
                bitarray_data, _ = compress_sequence(seq, reference_seq, m)
                temp_file_path = os.path.join(temp_output_folder, f"{os.path.basename(filename)}_m{m}.bin")
                with open(temp_file_path, "wb") as temp_file:
                    bitarray_data.tofile(temp_file)

                # Get the compressed size by checking the file size
                compressed_size = os.path.getsize(temp_file_path)  # Convert bytes to bits

                # Accumulate sizes
                total_original_size += original_size
                total_compressed_size += compressed_size

        # Calculate compression ratio for this m value
        if total_original_size > 0:
            compression_ratio = (total_original_size - total_compressed_size) / total_original_size
        else:
            compression_ratio = 0

        compression_ratios.append(compression_ratio)

    return m_values, compression_ratios

def plot_results(m_values, compression_ratios):
    """Plots the compression ratio for each m value."""
    plt.figure(figsize=(10, 6))
    plt.plot(m_values, compression_ratios, marker="o", linestyle="-", color="b")
    plt.title("Compression Ratio vs Golomb Parameter m for Real-World HBV Sequences")
    plt.xlabel("Golomb Parameter m")
    plt.ylabel("Compression Ratio")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Golomb encoding compression for different m values.")
    parser.add_argument("--input_folder", type=str, required=True, help="Folder containing the FASTA files to compress.")
    parser.add_argument("--reference_file", type=str, required=True, help="Reference FASTA file for compression.")
    parser.add_argument("--temp_output_folder", type=str, required=True, help="Temporary folder to store compressed files.")

    args = parser.parse_args()

    # Test compression and plot results
    m_values, compression_ratios = test_compression(args.input_folder, args.reference_file, args.temp_output_folder)
    plot_results(m_values, compression_ratios)