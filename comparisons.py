import os
import time
import glob
import subprocess
import matplotlib.pyplot as plt
from tqdm import tqdm
from golomb_encoding import compress_sequence  # Import the compress_sequence from golomb_encoding.py

def get_sequence_files(input_folder):
    """
    Get a list of sequence files (FASTA format) from the input folder.
    """
    return glob.glob(os.path.join(input_folder, "*.fasta"))

def compress_sequence_and_track(sequence_file, reference_file, identifier, m, output_folder):
    """
    Compress a single sequence using Golomb encoding and track time and size reduction.
    """
    # Get the original size of the sequence file
    original_size = os.path.getsize(sequence_file)

    # Start time tracking for compression
    start_time = time.time()

    # Read the sequence from the file
    with open(sequence_file, "r") as f:
        seq = f.read().strip()

    # Compress the sequence using Golomb encoding relative to the reference sequence
    reference_seq = open(reference_file, "r").read().strip()
    bitarray_data, _ = compress_sequence(seq, reference_seq, m)

    # Calculate the time taken for compression
    end_time = time.time()
    compression_time = end_time - start_time

    # Create a directory for this sequence if not already present
    sequence_output_folder = os.path.join(output_folder, os.path.basename(sequence_file).replace('.fasta', ''))
    os.makedirs(sequence_output_folder, exist_ok=True)

    # Save the compressed files in the sequence-specific folder
    compressed_file = os.path.join(sequence_output_folder, f"{identifier}_compressed.bin")
    with open(compressed_file, "wb") as f:
        bitarray_data.tofile(f)

    # Get the compressed size
    compressed_size = os.path.getsize(compressed_file)

    # Calculate compression rate (size reduction)
    compression_rate = (original_size - compressed_size) / original_size

    return compression_time, compression_rate, compressed_size, sequence_output_folder

def run_comparisons(input_folder, reference_file, identifier, m, output_folder):
    """
    Run the compression comparisons for all sequences in the input folder.
    """
    # List of sequence files in the input folder
    sequence_files = get_sequence_files(input_folder)

    # Store the results
    compression_times = []
    compression_rates = []
    sequence_names = []

    # Loop through each sequence file and compress it
    for sequence_file in tqdm(sequence_files, desc="Compressing sequences", unit="seq"):
        compression_time, compression_rate, _, _ = compress_sequence_and_track(sequence_file, reference_file, identifier, m, output_folder)
        compression_times.append(compression_time)
        compression_rates.append(compression_rate)
        sequence_names.append(os.path.basename(sequence_file))

    # Return the collected data
    return sequence_names, compression_times, compression_rates

def plot_compression_comparison(sequence_names, compression_rates, compression_times, identifier):
    """
    Visualize the compression comparison for all sequences with histograms.
    """
    # Create a histogram for compression rates
    plt.figure(figsize=(10, 5))
    plt.hist(compression_rates, bins=20, color='skyblue', edgecolor='black')
    plt.xlabel('Compression Rate')
    plt.ylabel('Frequency')
    plt.title(f'Compression Rate Distribution ({identifier})')
    plt.grid(False)  # Disable grid lines

    # Save the histogram figure
    plt.tight_layout()
    plt.savefig(f"{identifier}_compression_rates_histogram.png")
    plt.show()

    # Create a histogram for compression times
    plt.figure(figsize=(10, 5))
    plt.hist(compression_times, bins=20, color='lightcoral', edgecolor='black')
    plt.xlabel('Compression Time (seconds)')
    plt.ylabel('Frequency')
    plt.title(f'Compression Time Distribution ({identifier})')
    plt.grid(False)  # Disable grid lines

    # Save the histogram figure
    plt.tight_layout()
    plt.savefig(f"{identifier}_compression_times_histogram.png")
    plt.show()

def main():
    # Example parameters (you can modify this to accept command-line arguments)
    input_folder = "mtDNA_sequences"  # Folder with sequences
    reference_file = "ref_mtDNA.fasta"  # The reference file for Golomb encoding
    identifier = "mtDNA"  # Identifier for the dataset
    m = 128  # Golomb parameter (you can adjust this based on your data)
    output_folder = "compressed_output"  # Folder where all compressed files will be saved

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Run the compression comparisons
    sequence_names, compression_times, compression_rates = run_comparisons(input_folder, reference_file, identifier, m, output_folder)

    # Plot the results
    plot_compression_comparison(sequence_names, compression_rates, compression_times, identifier)

if __name__ == "__main__":
    main()



