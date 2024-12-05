import os
import time
import argparse
from Bio import Entrez, SeqIO
from hashlib import md5
from tqdm import tqdm  # Import tqdm for the progress bar

# Set email to comply with NCBI 
Entrez.email = "clarajeon126@gmail.com"

def get_ids(term, max_results=50, min_length=16000, max_length=17000, delay=0.5):
    """
    Search for specific DNA sequence IDs on NCBI and filter by sequence length in batches.
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

def fetch_sequences(ids, folder, identifier, delay=0.5):
    """
    Fetch and save unique sequences by their IDs, with a progress bar.
    """
    # Clear out the folder before downloading new files
    if os.path.exists(folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            os.remove(file_path)
        print(f"Cleared out existing files in {folder}")
    else:
        os.makedirs(folder, exist_ok=True)

    downloaded_hashes = set()  # To store MD5 hashes of downloaded sequences

    # Add tqdm progress bar over the list of IDs
    for record_id in tqdm(ids, desc="Downloading sequences", unit="seq"):
        with Entrez.efetch(db="nucleotide", id=record_id, rettype="fasta", retmode="text") as handle:
            record = SeqIO.read(handle, "fasta")
            
            # Calculate MD5 hash of the sequence to check for uniqueness
            sequence_hash = md5(str(record.seq).encode()).hexdigest()
            if sequence_hash in downloaded_hashes:
                print(f"\nDuplicate sequence found for ID {record_id}, skipping download.")
                continue  # Skip if this sequence is already downloaded
            
            # Save unique sequence with identifier as a prefix
            file_path = os.path.join(folder, f"{identifier}_{record_id}.fasta")
            with open(file_path, "w") as output_handle:
                SeqIO.write(record, output_handle, "fasta")
            
            # Add hash to the set of downloaded hashes
            downloaded_hashes.add(sequence_hash)
            print(f"\nDownloaded unique sequence for ID {record_id}")
        
        time.sleep(delay)  # Wait to avoid overwhelming the server

def main():
    parser = argparse.ArgumentParser(description="Download mitochondrial DNA sequences from NCBI based on search criteria.")
    parser.add_argument("--query", type=str, required=True, help="Search term for the Entrez query (e.g., 'Homo sapiens mitochondrion, complete genome')")
    parser.add_argument("--folder", type=str, required=True, help="Folder to save downloaded FASTA files")
    parser.add_argument("--identifier", type=str, required=True, help="Prefix identifier for downloaded file names")
    parser.add_argument("--max_results", type=int, default=50, help="Maximum number of sequence IDs to fetch (default: 50)")
    parser.add_argument("--min_length", type=int, default=16000, help="Minimum sequence length to keep (default: 16000)")
    parser.add_argument("--max_length", type=int, default=17000, help="Maximum sequence length to keep (default: 17000)")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay in seconds between API requests (default: 0.5)")

    args = parser.parse_args()

    # Fetch sequence IDs based on query and length criteria
    mtDNA_ids = get_ids(term=args.query, max_results=args.max_results, min_length=args.min_length, max_length=args.max_length, delay=args.delay)

    # Download and save unique sequences based on fetched IDs
    fetch_sequences(ids=mtDNA_ids, folder=args.folder, identifier=args.identifier, delay=args.delay)

if __name__ == "__main__":
    main()