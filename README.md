# CGFinalProject
Computational Genomics Final Project 

This project is designed to download, choose a reference, and compress DNA sequences using Golomb encoding. The workflow is managed through a `pipeline.py` script, which coordinates the other scripts to automate the process.

---

## Python Files

### 1. `download_data.py`
Downloads sequences from NCBI based on a specified query, filters them by length, and removes duplicates. It saves the sequences in a specified folder.

**Command-line arguments:**
- `--query`: The search term for NCBI (e.g., `"Homo sapiens mitochondrion, complete genome"`).
- `--folder`: Folder to save downloaded FASTA files (e.g., `"mtDNA_sequences"`).
- `--identifier`: Prefix for downloaded file names.
- `--max_results`: Maximum number of results to fetch (default: 1000).
- `--min_length`: Minimum nucleotide length for filtering sequences.
- `--max_length`: Maximum nucleotide length for filtering sequences.
- `--delay`: Delay in seconds between API requests to avoid server overload (default: 0.5).

**Example Usage:**
```bash
python download_data.py --query "Homo sapiens mitochondrion, complete genome" --folder "mtDNA_sequences" --identifier "mtDNA" --max_results 1000 --min_length 16000 --max_length 17000 --delay 0.5
```

### 2. `choose_ref.py`
Selects the best reference sequence from a specified folder of sequences by comparing similarity. It outputs the best reference sequence as a FASTA file.

**Command-line arguments:**
- `--input_folder`: Folder containing the FASTA files to analyze (e.g., `"mtDNA_sequences"`).
- `--identifier`: Identifier for naming the output reference file (e.g., `mtDNA`).

**Example Usage:**
```bash
python choose_ref.py --input_folder "mtDNA_sequences" --identifier "mtDNA"
```

### 3. `golomb_encoding.py`
Compresses each sequence from the specified folder relative to the reference sequence using Golomb encoding. Outputs three types of compressed files: differences strings, binary strings, and binary files.

**Command-line arguments:**
- `--input_folder`: Folder containing the FASTA files to compress (e.g., `"mtDNA_sequences"`).
- `--reference_file`: Reference FASTA file against which sequences will be compressed (e.g., `"ref_mtDNA.fasta"`).
- `--identifier`: Identifier used to name output folders and files (e.g., `mtDNA`).

**Example Usage:**
```bash
python golomb_encoding.py --input_folder "mtDNA_sequences" --reference_file "ref_mtDNA.fasta" --identifier "mtDNA"
```

### 4. `pipeline.py`
Automates the entire process by running `download_data.py`, `choose_ref.py`, and `golomb_encoding.py` in sequence, organizing all output files into a final folder named after the specified identifier.

**Command-line arguments:**
- `--query`: Search term for NCBI (e.g., `"Homo sapiens mitochondrion, complete genome"`).
- `--min_length`: Minimum sequence length for filtering.
- `--max_length`: Maximum sequence length for filtering.
- `--max_results`: Maximum number of results to fetch from NCBI.
- `--identifier`: Identifier for output folder and file naming (e.g., `mtDNA`).

**Example Usage:**
```bash
python pipeline.py --query "Homo sapiens mitochondrion, complete genome" --min_length 16000 --max_length 17000 --max_results 1000 --identifier "mtDNA"
```

---

## Data Folders

Each run of the pipeline organizes output folders under a main folder named `[identifier]`, which contains the following subfolders:

1. **`[identifier]_sequences`**: Folder for the downloaded sequences from `download_data.py`.
2. **`compressed_[identifier]_differences`**: Contains the intermediate text files with Golomb-encoded differences for each sequence relative to the reference.
3. **`compressed_[identifier]_binary_string`**: Contains the binary string representation of the compressed sequences.
4. **`compressed_[identifier]_binary_bin`**: Contains the final compressed sequences in binary format as `.bin` files for efficient storage.

---

## Notes
- The `choose_ref.py` script may take a long time to execute due to the sequence comparisons.
- The `bitarray` Python package is required for `golomb_encoding.py`. You can install it using:
  ```bash
  pip install bitarray
  ```
  
This project provides a pipeline for compressing DNA sequences, but it can be applied to various organisms and sequence types by changing the NCBI query in `download_data.py`.
```