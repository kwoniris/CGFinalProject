import subprocess
import os
import argparse
import shutil
# for MacOS
import sys

def delete_identifier_folder(identifier):
    """Delete the folder with the name of the identifier if it exists."""
    folder_path = identifier
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        shutil.rmtree(folder_path)
        print(f"Deleted existing folder: {folder_path}")

def run_download_data(query, min_length, max_length, max_results, identifier):
    """Run download_data.py with specified parameters."""
    command = [
        "python", "download_data.py",
        "--query", query,
        "--folder", f"{identifier}_sequences",
        "--identifier", identifier,
        "--max_results", str(max_results),
        "--min_length", str(min_length),
        "--max_length", str(max_length),
        "--delay", "0.5"
    ]
    subprocess.run(command, check=True)
    print("Finished running download_data.py")

def run_choose_ref(identifier):
    """Run choose_ref.py to find the best reference sequence."""
    command = [
        "python", "choose_ref.py",
        "--input_folder", f"{identifier}_sequences",
        "--identifier", identifier
    ]
    subprocess.run(command, check=True)
    print("Finished running choose_ref.py")

def run_golomb_encoding(identifier):
    """Run golomb_encoding.py to compress sequences."""
    command = [
        sys.executable, "golomb_encoding.py",
        "--input_folder", f"{identifier}_sequences",
        "--reference_file", f"ref_{identifier}.fasta",
        "--identifier", identifier
    ]
    subprocess.run(command, check=True)
    print("Finished running golomb_encoding.py")
    
def run_elias_gamma_encoding(identifier):
    """Run elias_gamma.py to compress sequences."""
    command = [
        ".venv/Scripts/python", "elias_gamma_encoding.py",
        "--input_folder", f"{identifier}_sequences",
        "--reference_file", f"ref_{identifier}.fasta",
        "--identifier", identifier
    ]
    subprocess.run(command, check=True)
    print("Finished running elias_gamma.py")

def organize_outputs(identifier):
    """Organize output folders into one large folder named after the identifier."""
    final_output_folder = identifier
    os.makedirs(final_output_folder, exist_ok=True)

    # List of folders to move into the main output folder
    output_folders = [
        f"compressed_{identifier}_differences",
        f"compressed_{identifier}_binary_string",
        f"compressed_{identifier}_binary_bin"
    ]
    
    # Move each folder into the final output directory
    for folder in output_folders:
        if os.path.exists(folder):
            shutil.move(folder, final_output_folder)
            print(f"Moved {folder} into {final_output_folder}")
        else:
            print(f"Warning: {folder} does not exist and was not moved.")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Pipeline for downloading data, choosing reference, and Golomb encoding.")
    parser.add_argument("--query", type=str, required=True, help="Search term for NCBI query (e.g., 'Homo sapiens mitochondrion, complete genome')")
    parser.add_argument("--min_length", type=int, required=True, help="Minimum sequence length to filter")
    parser.add_argument("--max_length", type=int, required=True, help="Maximum sequence length to filter")
    parser.add_argument("--max_results", type=int, required=True, help="Maximum number of results to fetch from NCBI")
    parser.add_argument("--identifier", type=str, required=True, help="Identifier for output folder and file naming")

    args = parser.parse_args()

    # Delete the identifier folder if it exists
    delete_identifier_folder(args.identifier)

    # Run each step of the pipeline
    run_download_data(args.query, args.min_length, args.max_length, args.max_results, args.identifier)
    run_choose_ref(args.identifier)
    
    # TODO: be able to do both at the same time
    run_golomb_encoding(args.identifier)
    #run_elias_gamma_encoding(args.identifier)

    # Organize all outputs into a single folder
    organize_outputs(args.identifier)
    print(f"Pipeline completed. All outputs are organized in the '{args.identifier}' folder.")
