import os
import time
import glob
import subprocess
import matplotlib.pyplot as plt
from tqdm import tqdm
from golomb_encoding import compress_sequence as golomb_compress  # Golomb compression
from elias_encoding import compress_sequence as elias_compress  # Elias compression

def get_sequence_files(input_folder):
    """
    Get a list of sequence files (FASTA format) from the input folder.
    """
    return glob.glob(os.path.join(input_folder, "*.fasta"))

def compress_sequence_and_track(sequence_file, reference_file, identifier, encoding_type, m, output_folder):
    """
    Compress a single sequence using the specified encoding type and track time and size reduction.
    """
    # Get the original size of the sequence file
    original_size = os.path.getsize(sequence_file)

    # Start time tracking for compression
    start_time = time.time()

    # Read the sequence from the file
    with open(sequence_file, "r") as f:
        seq = f.read().strip()

    # Compress the sequence using the selected encoding type
    reference_seq = open(reference_file, "r").read().strip()

    if encoding_type == "golomb":
        bitarray_data, _ = golomb_compress(seq, reference_seq, m)
    elif encoding_type == "gamma":
        bitarray_data, _ = elias_compress(seq, reference_seq, "gamma")
    elif encoding_type == "delta":
        bitarray_data, _ = elias_compress(seq, reference_seq, "delta")

    # Calculate the time taken for compression
    end_time = time.time()
    compression_time = end_time - start_time

    # Create a directory for this sequence if not already present
    sequence_output_folder = os.path.join(output_folder, os.path.basename(sequence_file).replace('.fasta', ''))
    os.makedirs(sequence_output_folder, exist_ok=True)

    # Save the compressed files in the sequence-specific folder
    compressed_file = os.path.join(sequence_output_folder, f"{identifier}_{encoding_type}_compressed.bin")
    with open(compressed_file, "wb") as f:
        bitarray_data.tofile(f)

    # Get the compressed size
    compressed_size = os.path.getsize(compressed_file)

    # Calculate compression rate (size reduction)
    compression_rate = (original_size - compressed_size) / original_size

    return compression_time, compression_rate, compressed_size, sequence_output_folder

def run_comparisons(input_folder, reference_file, identifier, m, output_folder):
    """
    Run the compression comparisons for all sequences in the input folder for each encoding type.
    """
    # List of sequence files in the input folder
    sequence_files = get_sequence_files(input_folder)

    # Store the results for each encoding type
    compression_times = {"golomb": [], "gamma": [], "delta": []}
    compression_rates = {"golomb": [], "gamma": [], "delta": []}
    sequence_names = []

    # Loop through each sequence file and compress it
    for sequence_file in tqdm(sequence_files, desc="Compressing sequences", unit="seq"):
        for encoding_type in ["golomb", "gamma", "delta"]:
            # Compress using the specified encoding type
            compression_time, compression_rate, compressed_size, sequence_output_folder = compress_sequence_and_track(
                sequence_file, reference_file, identifier, encoding_type, m, output_folder
            )

            # Store results for each encoding type
            compression_times[encoding_type].append(compression_time)
            compression_rates[encoding_type].append(compression_rate)

        sequence_names.append(os.path.basename(sequence_file))

    # Return the collected data
    return sequence_names, compression_times, compression_rates

def plot_compression_comparison(sequence_names, compression_rates, compression_times, identifier):
    """
    Visualize the compression comparison for all sequences with histograms.
    """
    # Set up colors for the three algorithms
    colors = {
        "golomb": 'palevioletred',
        "gamma": 'skyblue',
        "delta": 'sandybrown'
    }

    # Create the figure and axis
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Plot Compression Rate Histogram
    for encoding_type in compression_rates:
        axes[0].hist(compression_rates[encoding_type], bins=20, color=colors[encoding_type], alpha=0.7, label=f'{encoding_type.capitalize()}')
    axes[0].set_xlabel('Compression Rate')
    axes[0].set_ylabel('Frequency')
    axes[0].set_title(f'Compression Rate Distribution ({identifier})')
    axes[0].legend()
    axes[0].grid(False)  # Disable grid lines

    # Plot Compression Time Histogram
    for encoding_type in compression_times:
        axes[1].hist(compression_times[encoding_type], bins=20, color=colors[encoding_type], alpha=0.7, label=f'{encoding_type.capitalize()}')
    axes[1].set_xlabel('Compression Time (seconds)')
    axes[1].set_ylabel('Frequency')
    axes[1].set_title(f'Compression Time Distribution ({identifier})')
    axes[1].legend()
    axes[1].grid(False)  # Disable grid lines

    # Save the figure with both histograms
    plt.tight_layout()
    plt.savefig(f"{identifier}_compression_comparison.png")
    plt.show()

def main():
    # Example parameters
    input_folders = {
        "mtDNA": "mtDNA_sequences",
        "HBV": "HBV_sequences"
    }
    reference_files = {
        "mtDNA": "ref_mtDNA.fasta",
        "HBV": "ref_HBV.fasta"
    }
    m = 128  # Golomb parameter (adjust based on your data)
    output_folder = "compressed_output"  # Folder where all compressed files will be saved

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Loop through both datasets
    for identifier in input_folders:
        input_folder = input_folders[identifier]
        reference_file = reference_files[identifier]

        # Run the compression comparisons
        sequence_names, compression_times, compression_rates = run_comparisons(
            input_folder, reference_file, identifier, m, output_folder)

        # Plot the results
        plot_compression_comparison(sequence_names, compression_rates, compression_times, identifier)

if __name__ == "__main__":
    main()

