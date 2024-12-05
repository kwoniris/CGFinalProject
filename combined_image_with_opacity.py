# import numpy as np
# from PIL import Image
# import os
# import argparse

# # def calculate_opacity(images):
# #     """
# #     Calculates per-pixel opacity based on similarity across images.

# #     Args:
# #     - images (list of np.ndarray): List of image arrays.

# #     Returns:
# #     - opacity_map (np.ndarray): An array of opacity values (0-1) for each pixel.
# #     """
# #     num_images = len(images)
# #     stacked_images = np.stack(images, axis=-1)  # Shape: (H, W, C, num_images)

# #     # Calculate mean and variance of RGB values across images
# #     mean_image = np.mean(stacked_images, axis=-1)
# #     variance_image = np.var(stacked_images, axis=-1)

# #     # Normalize variance to 0-1 for opacity
# #     max_variance = np.max(variance_image)
# #     opacity_map = 1 - (variance_image / max_variance)  # Higher similarity = Higher opacity

# #     print("Here 1")

# #     return opacity_map


# # def generate_combined_image_with_opacity(input_folder, output_path):
# #     """
# #     Combines images with opacity determined by similarity.

# #     Args:
# #     - input_folder (str): Path to the folder containing images.
# #     - output_path (str): Path to save the final combined image.
# #     """
# #     # Load images as arrays
# #     image_files = [f for f in os.listdir(input_folder) if f.endswith(".png")]
# #     images = [np.array(Image.open(os.path.join(input_folder, f))) for f in image_files]

# #     # Calculate per-pixel opacity
# #     opacity_map = calculate_opacity(images)
# #     print("Here 2")

# #     # Combine images with opacity
# #     combined_image = np.zeros_like(images[0], dtype=np.float32)
# #     for img in images:
# #         combined_image += img * opacity_map[..., None]  # Apply opacity to each image

# #     # Normalize the combined image to 0-255
# #     combined_image = (combined_image / len(images)).clip(0, 255).astype(np.uint8)
# #     print("Here 3")

# #     # Save the combined image
# #     img = Image.fromarray(combined_image, "RGB")
# #     img.save(output_path)
# #     print(f"Saved combined image with opacity to {output_path}")


# # def main():
# #     # Parse command-line arguments
# #     parser = argparse.ArgumentParser(
# #         description="Combine images with opacity determined by pixel similarity."
# #     )
# #     parser.add_argument(
# #         "--input_folder", required=True, help="Path to the folder containing input images."
# #     )
# #     parser.add_argument(
# #         "--output_path", required=True, help="Path to save the output combined image."
# #     )

# #     args = parser.parse_args()

# #     # Run the main function
# #     generate_combined_image_with_opacity(args.input_folder, args.output_path)


# # if __name__ == "__main__":
# #     main()

# import numpy as np
# from PIL import Image, UnidentifiedImageError
# import os
# import argparse


# def calculate_opacity(images):
#     """
#     Calculates per-pixel opacity based on similarity across images.

#     Args:
#     - images (list of np.ndarray): List of image arrays.

#     Returns:
#     - opacity_map (np.ndarray): An array of opacity values (0-1) for each pixel.
#     """
#     num_images = len(images)
#     stacked_images = np.stack(images, axis=-1)  # Shape: (H, W, C, num_images)

#     # Calculate mean and variance of RGB values across images
#     mean_image = np.mean(stacked_images, axis=-1)
#     variance_image = np.var(stacked_images, axis=-1)

#     # Normalize variance to 0-1 for opacity
#     max_variance = np.max(variance_image)
#     opacity_map = 1 - (variance_image / max_variance)  # Higher similarity = Higher opacity

#     print("Calculated opacity map.")
#     return opacity_map


# def generate_combined_image_with_opacity(input_folder, output_path):
#     """
#     Combines images with opacity determined by similarity.

#     Args:
#     - input_folder (str): Path to the folder containing images.
#     - output_path (str): Path to save the final combined image.
#     """
#     # Load images as arrays with error handling
#     image_files = [f for f in os.listdir(input_folder) if f.endswith(".png")]
#     images = []
#     for f in image_files:
#         image_path = os.path.join(input_folder, f)
#         try:
#             img = Image.open(image_path)
#             images.append(np.array(img))
#         except UnidentifiedImageError:
#             print(f"Error: Cannot identify image file '{image_path}'. Skipping.")
#         except Exception as e:
#             print(f"Error: Failed to process '{image_path}'. Reason: {e}")

#     if not images:
#         print("No valid images found in the input folder.")
#         return

#     # Calculate per-pixel opacity
#     opacity_map = calculate_opacity(images)
#     print("Generated opacity map.")

#     # Combine images with opacity
#     combined_image = np.zeros_like(images[0], dtype=np.float32)
#     for img in images:
#         combined_image += img * opacity_map[..., None]  # Apply opacity to each image

#     # Normalize the combined image to 0-255
#     combined_image = (combined_image / len(images)).clip(0, 255).astype(np.uint8)
#     print("Combined image created.")

#     # Save the combined image
#     img = Image.fromarray(combined_image, "RGB")
#     img.save(output_path)
#     print(f"Saved combined image with opacity to {output_path}")


# def main():
#     # Parse command-line arguments
#     parser = argparse.ArgumentParser(
#         description="Combine images with opacity determined by pixel similarity."
#     )
#     parser.add_argument(
#         "--input_folder", required=True, help="Path to the folder containing input images."
#     )
#     parser.add_argument(
#         "--output_path", required=True, help="Path to save the output combined image."
#     )

#     args = parser.parse_args()

#     # Run the main function
#     generate_combined_image_with_opacity(args.input_folder, args.output_path)


# if __name__ == "__main__":
#     main()

import os
import numpy as np
from PIL import Image, UnidentifiedImageError
import argparse


def calculate_opacity(images):
    """
    Calculates per-pixel opacity based on similarity across images.

    Args:
    - images (list of np.ndarray): List of image arrays (all of the same size).

    Returns:
    - opacity_map (np.ndarray): A 2D array of opacity values (0-1) for each pixel.
    """
    # Stack images along a new dimension (shape: H x W x C x num_images)
    stacked_images = np.stack(images, axis=-1)

    # Calculate variance of RGB values across images for each pixel
    variance_image = np.var(stacked_images, axis=-1)  # Variance along the last dimension

    # Normalize variance to 0-1 (low variance -> high opacity)
    max_variance = np.max(variance_image)
    if max_variance > 0:
        opacity_map = 1 - (variance_image / max_variance)  # Higher similarity -> Higher opacity
    else:
        opacity_map = np.ones_like(variance_image)  # All images are identical, full opacity

    return opacity_map


def generate_combined_image_with_opacity(input_folder, output_path):
    """
    Combines images with opacity determined by similarity.

    Args:
    - input_folder (str): Path to the folder containing images.
    - output_path (str): Path to save the final combined image.
    """
    # Load images as arrays with error handling
    image_files = [f for f in os.listdir(input_folder) if f.endswith(".png")]
    images = []
    for f in image_files:
        image_path = os.path.join(input_folder, f)
        try:
            img = Image.open(image_path)
            images.append(np.array(img, dtype=np.float32))  # Convert to float32 for scaling
        except UnidentifiedImageError:
            print(f"Error: Cannot identify image file '{image_path}'. Skipping.")
        except Exception as e:
            print(f"Error: Failed to process '{image_path}'. Reason: {e}")

    if not images:
        print("No valid images found in the input folder.")
        return

    # Calculate per-pixel opacity
    opacity_map = calculate_opacity(images)  # Shape: (H, W)
    print("Generated opacity map.")

    # Add a channel dimension to opacity_map to match the image shape
    opacity_map = opacity_map[..., None]  # Shape: (H, W, 1)

    # Combine images with opacity
    combined_image = np.zeros_like(images[0], dtype=np.float32)
    for img in images:
        # Preserve the color values while scaling by opacity
        combined_image += img * opacity_map  # Each image contributes proportionally to opacity

    # Normalize the combined image to 0-255
    combined_image = combined_image.clip(0, 255).astype(np.uint8)
    print("Combined image created.")

    # Save the combined image
    img = Image.fromarray(combined_image, "RGB")
    img.save(output_path)
    print(f"Saved combined image with opacity to {output_path}")


if __name__ == "__main__":
    # Command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Combine images into one image with opacity based on similarity."
    )
    parser.add_argument(
        "--input_folder", required=True, help="Folder containing images to combine."
    )
    parser.add_argument(
        "--output_path", required=True, help="Path to save the combined image."
    )

    args = parser.parse_args()

    # Run the combination process
    generate_combined_image_with_opacity(args.input_folder, args.output_path)
