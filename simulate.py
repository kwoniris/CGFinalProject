import os
from Bio import SeqIO
import numpy as np  # Use numpy for geometric distribution

# Function to introduce geometric-distributed SNPs in a sequence
def introduce_geometric_snps(reference, p, num_sequences):
    sequences = []
    for _ in range(num_sequences):
        new_seq = list(reference)
        index = 0
        while index < len(reference):
            # Generate the next position difference using numpy's geometric distribution
            skip = np.random.geometric(p)
            index += skip
            if index >= len(reference):
                break

            # Introduce a SNP: Replace the base with a random nucleotide different from the original
            original_base = reference[index]
            new_base = np.random.choice([b for b in "ACGT" if b != original_base])
            new_seq[index] = new_base

        sequences.append("".join(new_seq))

    return sequences

# Main function to read a FASTA file and generate simulated sequences
def generate_sequences(fasta_file, p, num_sequences, output_folder):
    with open(fasta_file, "r") as handle:
        records = list(SeqIO.parse(handle, "fasta"))

    if not records:
        raise ValueError("No sequences found in the provided FASTA file.")

    reference_seq = str(records[0].seq)  # Use the first sequence as the reference

    # Generate sequences with geometric-distributed SNPs
    simulated_sequences = introduce_geometric_snps(reference_seq, p, num_sequences)

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Write each simulated sequence to its own FASTA file
    for i, seq in enumerate(simulated_sequences):
        output_file = os.path.join(output_folder, f"simHBV_{i+1}.fasta")
        with open(output_file, "w") as output_handle:
            output_handle.write(f">simHBV_{i+1}\n")
            output_handle.write(f"{seq}\n")

    print(f"Simulated sequences written to folder: {output_folder}")

# Example usage
fasta_file = "ref_sample.fasta"  # Replace with your reference FASTA file
output_folder = "sample_sequences"  # Folder to store the output FASTA files
p = 0.1  # Probability parameter for geometric distribution
num_sequences = 15

generate_sequences(fasta_file, p, num_sequences, output_folder)