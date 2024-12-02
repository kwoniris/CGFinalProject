import os
import qrcode
from qrcode.image.pil import PilImage
import random
import argparse

def unique_color(seed_value):
    """
    Generates a unique color based on a seed value.
    
    Args:
    - seed_value (int): Seed to generate the color.
    
    Returns:
    - Tuple of RGB values.
    """
    random.seed(seed_value)
    return random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)

def bin_to_colorful_qr(input_folder, output_folder, identifier):
    """
    Converts binary .bin files to unique colorful QR code images.
    
    Args:
    - input_folder (str): Path to the folder containing .bin files.
    - output_folder (str): Path to save QR code images.
    - identifier (str): Identifier for naming output files.
    """
    os.makedirs(output_folder, exist_ok=True)

    # List all .bin files in the input folder
    bin_files = [f for f in os.listdir(input_folder) if f.endswith('.bin')]

    # Debugging: Print out the files found
    print(f"Found {len(bin_files)} .bin files in the folder.")
    print("List of files:", bin_files)

    # Check if bin_files is empty
    if not bin_files:
        print("No .bin files found in the specified folder. Please check the path.")
        return

    for idx, bin_file in enumerate(bin_files):
        bin_path = os.path.join(input_folder, bin_file)
        
        # Read binary content
        with open(bin_path, 'rb') as f:
            binary_data = f.read()

        # Create a QR code with unique colors
        qr = qrcode.QRCode(
            version=1,  # Start with version 1
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        # Dynamically set the QR code version based on the size of the data
        # The maximum size for a QR code version 40 is around 2953 bytes
        max_version = 40
        data_length = len(binary_data)

        # Set the QR code version based on data length, ensuring it doesn't exceed version 40
        if data_length > 2953:  # Max bytes for version 40
            qr.version = 40
        elif data_length > 2334:  # Max bytes for version 39
            qr.version = 39
        elif data_length > 2089:  # Max bytes for version 38
            qr.version = 38
        # You can continue this pattern if needed, but this should be sufficient

        # Adding the binary data to the QR code
        qr.add_data(binary_data)
        qr.make(fit=True)
        
        # Generate unique color for the fill (foreground) and background
        fill_color = unique_color(idx)  # Unique color based on file index
        back_color = (255, 255, 255)  # White background
        
        # Create QR code image with unique colors
        img = qr.make_image(image_factory=PilImage, fill_color=fill_color, back_color=back_color)

        # Save the QR code image
        output_filename = f"{identifier}_{os.path.splitext(bin_file)[0]}.png"
        output_path = os.path.join(output_folder, output_filename)
        img.save(output_path)
        print(f"Saved colorful QR code to {output_path}")

if __name__ == "__main__":
    # Command-line argument parsing
    parser = argparse.ArgumentParser(description="Convert binary .bin files to unique colorful QR code images.")
    parser.add_argument("--input_folder", required=True, help="Folder containing .bin files.")
    parser.add_argument("--output_folder", required=True, help="Folder to save QR code images.")
    parser.add_argument("--identifier", required=True, help="Identifier for naming output files.")
    
    args = parser.parse_args()
    bin_to_colorful_qr(args.input_folder, args.output_folder, args.identifier)
