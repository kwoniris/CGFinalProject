import os
import argparse
from Bio import SeqIO
import numpy as np

def find_best_reference(input_folder, identifier):
    # Store sequences and their respective file names from FASTA files into arrays
    sequences = []
    filenames = []

    for filename in os.listdir(input_folder):
        if filename.endswith(".fasta"):
            input_path = os.path.join(input_folder, filename)
            record = SeqIO.read(input_path, "fasta")
            sequences.append(str(record.seq)) 
            filenames.append(filename)

    # Differences stored in a symmetric matrix
    num_sequences = len(sequences)
    differences_matrix = np.zeros((num_sequences, num_sequences), dtype=int)

    for i in range(num_sequences):
        for j in range(i + 1, num_sequences):
            differences = sum(1 for a, b in zip(sequences[i], sequences[j]) if a != b)
            differences_matrix[i, j] = differences
            differences_matrix[j, i] = differences 

    # Get average difference
    average_differences = differences_matrix.sum(axis=1) / (num_sequences - 1)

    # Find the index of the sequence with the smallest average difference
    best_reference_index = np.argmin(average_differences)
    best_reference_filename = filenames[best_reference_index]
    best_reference_sequence = sequences[best_reference_index]

    print(f"The best reference sequence is '{best_reference_filename}' with an average difference of {average_differences[best_reference_index]:.2f} differences from other sequences.")

    # Save the best reference sequence to a new file
    output_filename = f"ref_{identifier}.fasta"
    with open(output_filename, "w") as output_handle:
        output_handle.write(f">{best_reference_filename}\n{best_reference_sequence}")
    print(f"Best reference sequence saved as '{output_filename}'")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Find the best reference sequence based on sequence similarity.")
    parser.add_argument("--input_folder", type=str, required=True, help="Input folder containing the FASTA files to analyze.")
    parser.add_argument("--identifier", type=str, required=True, help="Identifier to use in the output reference file name (e.g., 'mtdna').")

    args = parser.parse_args()
    
    # Run the function to find the best reference
    find_best_reference(args.input_folder, args.identifier)