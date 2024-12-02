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

def bin_to_colorful_image(input_folder, output_folder, identifier, reference_file):
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

        # Determine image dimensions
        diff_length = len(diff_data)
        image_size = int(np.ceil(np.sqrt(diff_length)))
        total_pixels = image_size ** 2

        # Pad diff_data to ensure it fills a complete square
        padded_diff_data = list(diff_data) + [0] * (total_pixels - diff_length)
        assert len(padded_diff_data) == total_pixels, "Padding failed: Incorrect total pixels"

        # Convert to a NumPy array and reshape into an image
        diff_array = np.array(padded_diff_data, dtype=np.uint8).reshape((image_size, image_size))
        assert diff_array.shape == (image_size, image_size), "Reshaping failed: Incorrect shape"

        # Map binary differences to RGB colors
        image_array = np.zeros((image_size, image_size, 3), dtype=np.uint8)
        for i, value in enumerate(diff_array.flatten()):
            row, col = divmod(i, image_size)
            int_value = int(value)  # Explicitly cast to int to handle overflow safely
            image_array[row, col] = (
                np.clip(int_value, 0, 255),                 # Red channel
                np.clip(255 - int_value, 0, 255),          # Green channel
                np.clip((int_value * 2) % 256, 0, 255)     # Blue channel
            )

        # Convert the NumPy array to an image
        img = Image.fromarray(image_array, 'RGB')

        # Save the image
        output_filename = f"{identifier}_{os.path.splitext(bin_file)[0]}_colorful.png"
        output_path = os.path.join(output_folder, output_filename)
        
        try:
            with open(output_path, "wb") as f:
                img.save(f, format="PNG")
            print(f"Image saved successfully: {output_path}")
        except Exception as e:
            print(f"Failed to save image: {e}")

        print(f"Saved colorful difference image to {output_path}")

if __name__ == "__main__":
    # Command-line argument parsing
    parser = argparse.ArgumentParser(description="Convert binary .bin files to unique colorful QR code images based on differences to a reference FASTA file.")
    parser.add_argument("--input_folder", required=True, help="Folder containing .bin files.")
    parser.add_argument("--output_folder", required=True, help="Folder to save QR code images.")
    parser.add_argument("--identifier", required=True, help="Identifier for naming output files.")
    parser.add_argument("--reference_file", required=True, help="Path to the reference FASTA file for comparison.")
    
    args = parser.parse_args()
    bin_to_colorful_image(args.input_folder, args.output_folder, args.identifier, args.reference_file)
