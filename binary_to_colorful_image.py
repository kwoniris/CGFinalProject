import os
import numpy as np
from PIL import Image
import math
import argparse


def calculate_max_dimensions(input_folder):
    """
    Calculates the maximum dimensions required to standardize all images.

    Args:
    - input_folder (str): Path to the folder containing binary files.

    Returns:
    - max_size (int): The standardized size for all images (square dimensions).
    """
    max_pixels = 0
    binary_files = [f for f in os.listdir(input_folder) if f.endswith(".bin")]

    for binary_file in binary_files:
        binary_file_path = os.path.join(input_folder, binary_file)
        with open(binary_file_path, "rb") as f:
            binary_data = f.read()
        num_pixels = len(binary_data) // 3  # Each pixel requires 3 bytes
        max_pixels = max(max_pixels, num_pixels)

    # Calculate the closest square size
    max_size = math.ceil(math.sqrt(max_pixels))
    return max_size


def binary_to_color_image(binary_file, output_folder, image_name, standardized_size):
    """
    Converts binary data to a color image based on 3-byte chunks, standardized to a given size.

    Args:
    - binary_file (str): Path to the binary file.
    - output_folder (str): Path to save the output image.
    - image_name (str): Name of the output image (without extension).
    - standardized_size (int): Standardized square dimensions for the image.
    """
    with open(binary_file, "rb") as f:
        binary_data = f.read()

    # Convert binary data to RGB values (3-byte chunks)
    chunks = [binary_data[i:i+3] for i in range(0, len(binary_data), 3)]
    rgb_colors = [
        (chunk[0], chunk[1] if len(chunk) > 1 else 0, chunk[2] if len(chunk) > 2 else 0)
        for chunk in chunks
    ]

    # Pad with black (0, 0, 0) to fit the standardized size
    num_pixels = len(rgb_colors)
    padded_colors = rgb_colors + [(0, 0, 0)] * (standardized_size**2 - num_pixels)

    # Create the image array
    image_array = np.array(padded_colors, dtype=np.uint8).reshape((standardized_size, standardized_size, 3))

    # Save the image
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, f"{image_name}.png")
    try:
        with open(output_path, "wb") as f:
            img = Image.fromarray(image_array, 'RGB')
            img.save(f, format="PNG")
            print(f"Image saved successfully: {output_path}")
    except Exception as e:
        print(f"Failed to save image {output_path}: {e}")


def process_all_binary_files(input_folder, output_folder):
    """
    Processes all binary files in the input folder and generates standardized color images.

    Args:
    - input_folder (str): Path to the folder containing binary files.
    - output_folder (str): Path to the folder to save the output images.
    """
    # Calculate the max dimensions for all images
    print("Calculating maximum dimensions for standardizing images...")
    standardized_size = calculate_max_dimensions(input_folder)
    print(f"Standardized size for all images: {standardized_size}x{standardized_size}")

    # Process each binary file
    binary_files = [f for f in os.listdir(input_folder) if f.endswith(".bin")]
    if not binary_files:
        print("No .bin files found in the specified folder.")
        return

    for binary_file in binary_files:
        binary_file_path = os.path.join(input_folder, binary_file)
        image_name = os.path.splitext(binary_file)[0]  # Remove .bin extension
        binary_to_color_image(binary_file_path, output_folder, image_name, standardized_size)

    print("Finished processing all binary files.")


if __name__ == "__main__":
    # Command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Convert binary .bin files to standardized color images."
    )
    parser.add_argument(
        "--input_folder", required=True, help="Folder containing binary files (.bin)."
    )
    parser.add_argument(
        "--output_folder", required=True, help="Folder to save generated color images."
    )

    args = parser.parse_args()

    # Process binary files
    process_all_binary_files(args.input_folder, args.output_folder)
