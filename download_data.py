# download_data.py

import os
import time
import argparse
from Bio import Entrez, SeqIO
from hashlib import md5

# Set your email to comply with NCBI requirements
Entrez.email = "clarajeon126@gmail.com"  # Replace with your actual email

def get_ids(term, max_results=50, min_length=16000, max_length=17000, delay=0.5):
    """
    Search for specific DNA sequence IDs on NCBI and filter by sequence length in batches.

    :param term: The search term for mtDNA sequences
    :param max_results: Maximum number of sequence IDs to fetch in total
    :param min_length: Minimum length of sequences to keep
    :param max_length: Maximum length of sequences to keep
    :param delay: Delay in seconds between requests to avoid timeout
    :return: A list of sequence IDs that meet the length requirement
    """
    print(f"Searching for: {term}")

    # Initial search to get a broad list of IDs
    with Entrez.esearch(db="nucleotide", term=term, retmax=max_results) as handle:
        record = Entrez.read(handle)
        all_ids = record["IdList"]
    
    print(f"Fetched {len(all_ids)} IDs initially.")
    
    # Filter IDs based on sequence length in batches
    filtered_ids = []
    batch_size = 10  # Number of IDs to process in each batch
    
    for i in range(0, len(all_ids), batch_size):
        batch_ids = all_ids[i:i+batch_size]
        
        # Fetch summaries for each batch of IDs
        with Entrez.esummary(db="nucleotide", id=",".join(batch_ids)) as handle:
            summaries = Entrez.read(handle)
        
        # Filter by length
        for summary in summaries:
            sequence_length = int(summary["Length"])
            if min_length <= sequence_length <= max_length:
                filtered_ids.append(summary["Id"])
                print(f"ID {summary['Id']} meets length requirement: {sequence_length} bp")
        
        time.sleep(delay)  # Wait to avoid overwhelming the server
    
    print(f"{len(filtered_ids)} IDs meet the length requirement between {min_length} and {max_length} bp.")
    return filtered_ids

def fetch_sequences(ids, folder, identifier, test_id=None, delay=0.5):
    """
    Fetch and save unique sequences by their IDs. Optionally, save one specific sequence as a test file.
    :param ids: List of sequence IDs
    :param folder: Directory to save FASTA files
    :param identifier: Prefix identifier for file names
    :param test_id: Specific ID to save in a separate test_data folder
    :param delay: Delay in seconds between requests to avoid timeout
    """
    # Clear out the folder before downloading new files
    if os.path.exists(folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            os.remove(file_path)
        print(f"Cleared out existing files in {folder}")
    else:
        os.makedirs(folder, exist_ok=True)

    if test_id:
        os.makedirs("test_data", exist_ok=True)  # Create test_data folder if test_id is provided

    downloaded_hashes = set()  # To store MD5 hashes of downloaded sequences

    for record_id in ids:
        with Entrez.efetch(db="nucleotide", id=record_id, rettype="fasta", retmode="text") as handle:
            record = SeqIO.read(handle, "fasta")
            
            # Calculate MD5 hash of the sequence to check for uniqueness
            sequence_hash = md5(str(record.seq).encode()).hexdigest()
            if sequence_hash in downloaded_hashes:
                print(f"Duplicate sequence found for ID {record_id}, skipping download.")
                continue  # Skip if this sequence is already downloaded
            
            # Save unique sequence with identifier as a prefix
            file_path = os.path.join(folder, f"{identifier}_{record_id}.fasta")
            with open(file_path, "w") as output_handle:
                SeqIO.write(record, output_handle, "fasta")
            
            # Add hash to the set of downloaded hashes
            downloaded_hashes.add(sequence_hash)
            print(f"Downloaded unique sequence for ID {record_id}")

            # If this ID matches test_id, save it in test_data folder with _test suffix
            if test_id and record_id == test_id:
                test_file_path = os.path.join("test_data", f"{identifier}_test.fasta")
                with open(test_file_path, "w") as test_output_handle:
                    SeqIO.write(record, test_output_handle, "fasta")
                print(f"Saved test sequence for ID {record_id} as {test_file_path}")
        
        time.sleep(delay)  # Wait to avoid overwhelming the server

def main():
    parser = argparse.ArgumentParser(description="Download DNA sequences from NCBI based on search criteria.")
    parser.add_argument("--query", type=str, required=True, help="Search term for the Entrez query (e.g., 'Homo sapiens mitochondrion, complete genome')")
    parser.add_argument("--folder", type=str, required=True, help="Folder to save downloaded FASTA files")
    parser.add_argument("--identifier", type=str, required=True, help="Prefix identifier for downloaded file names")
    parser.add_argument("--max_results", type=int, default=50, help="Maximum number of sequence IDs to fetch (default: 50)")
    parser.add_argument("--min_length", type=int, default=16000, help="Minimum sequence length to keep (default: 16000)")
    parser.add_argument("--max_length", type=int, default=17000, help="Maximum sequence length to keep (default: 17000)")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay in seconds between API requests (default: 0.5)")
    parser.add_argument("--test_id", type=str, help="Specific sequence ID to save as a test file in test_data folder")

    args = parser.parse_args()

    # Fetch sequence IDs based on query and length criteria
    mtDNA_ids = get_ids(term=args.query, max_results=args.max_results, min_length=args.min_length, max_length=args.max_length, delay=args.delay)

    # Download and save unique sequences based on fetched IDs
    fetch_sequences(ids=mtDNA_ids, folder=args.folder, identifier=args.identifier, test_id=args.test_id, delay=args.delay)

if __name__ == "__main__":
    main()
