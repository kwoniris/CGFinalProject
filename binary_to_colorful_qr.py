import os
import qrcode
from qrcode.image.pil import PilImage
import random
import argparse
from PIL import Image


# def unique_color(seed_value):
#     """
#     Generates a unique color based on a seed value.
    
#     Args:
#     - seed_value (int): Seed to generate the color.
    
#     Returns:
#     - Tuple of RGB values.
#     """
#     random.seed(seed_value)
#     return random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)

def fasta_to_binary(fasta_file):
    """
    Converts a FASTA file to binary format by encoding its content.
    
    Args:
    - fasta_file (str): Path to the FASTA file.
    
    Returns:
    - bytes: The binary content of the FASTA file.
    """
    with open(fasta_file, 'r') as file:
        fasta_data = file.read()
    return bytes(fasta_data, 'utf-8')

def compute_diff(binary_data, reference_data):
    """
    Computes the XOR difference between two binary data sequences.
    
    Args:
    - binary_data (bytes): The binary data to compare.
    - reference_data (bytes): The reference binary data.
    
    Returns:
    - bytes: The XOR result highlighting the differences.
    """
    # XOR the binary data with the reference data
    diff_data = bytes(a ^ b for a, b in zip(binary_data, reference_data))
    return diff_data

def bin_to_colorful_qr(input_folder, output_folder, identifier, reference_file):
    import numpy as np
    os.makedirs(output_folder, exist_ok=True)

    # List all .bin files in the input folder
    bin_files = [f for f in os.listdir(input_folder) if f.endswith('.bin')]

    if not bin_files:
        print("No .bin files found in the specified folder. Please check the path.")
        return

    # Load the reference FASTA file and convert it to binary
    reference_data = fasta_to_binary(reference_file)

    # Process each .bin file in the input folder
    for idx, bin_file in enumerate(bin_files):
        bin_path = os.path.join(input_folder, bin_file)
        
        # Read binary content of the file
        with open(bin_path, 'rb') as f:
            binary_data = f.read()

        # Compute the XOR difference between the binary file and the reference file
        diff_data = compute_diff(binary_data, reference_data)

        # Create a QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(diff_data)
        qr.make(fit=True)

        # Extract the QR matrix
        qr_matrix = qr.modules
        size = len(qr_matrix)

        # Create an image array
        img_array = np.zeros((size * qr.box_size, size * qr.box_size, 3), dtype=np.uint8)
        
        # Map binary data to pixel colors
        diff_values = list(diff_data)  # Convert byte data to a list of integers
        diff_colors = [
            (value, 255 - value, (value * 2) % 255)  # Example: RGB based on XOR value
            for value in diff_values
        ]

        # Fill the image array with colors
        color_idx = 0  # Index to traverse the diff_colors
        for y, row in enumerate(qr_matrix):
            for x, val in enumerate(row):
                if val:  # If the module (QR pixel) is black
                    if color_idx < len(diff_colors):
                        color = diff_colors[color_idx]
                        color_idx += 1
                    else:
                        color = (0, 0, 0)  # Default to black if out of diff_data
                    for i in range(qr.box_size):
                        for j in range(qr.box_size):
                            img_array[
                                y * qr.box_size + i, x * qr.box_size + j
                            ] = color

        # Convert the numpy array to an image
        img = Image.fromarray(img_array, 'RGB')

        # Save the image
        output_filename = f"{identifier}_{os.path.splitext(bin_file)[0]}_diff_colorful.png"
        output_path = os.path.join(output_folder, output_filename)
        img.save(output_path)
        print(f"Saved colorful QR code with diff representation to {output_path}")

if __name__ == "__main__":
    # Command-line argument parsing
    parser = argparse.ArgumentParser(description="Convert binary .bin files to unique colorful QR code images based on differences to a reference FASTA file.")
    parser.add_argument("--input_folder", required=True, help="Folder containing .bin files.")
    parser.add_argument("--output_folder", required=True, help="Folder to save QR code images.")
    parser.add_argument("--identifier", required=True, help="Identifier for naming output files.")
    parser.add_argument("--reference_file", required=True, help="Path to the reference FASTA file for comparison.")
    
    args = parser.parse_args()
    bin_to_colorful_qr(args.input_folder, args.output_folder, args.identifier, args.reference_file)
