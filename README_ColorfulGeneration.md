# CGFinalProject Part 2 
## Colorful QR Code Generation from Binary Files

This project takes binary files as input, compares them byte by byte to the reference FASTA sequence identified from previous `pipeline.py`, and generates colorful QR code image representing the differences between each binary file and the reference. The colors are unique for each file. 

---
## Prerequisites
Before running the script, ensure that the following dependencies are installed:

- **Python 3.x** (preferably Python 3.9 or higher)
- **Required Python Libraries**:
  - `qrcode`: For generating QR codes.
  - `Pillow`: Required by `qrcode` to generate images.
  - `argparse`: For handling command-line arguments.
  
You can install the required libraries using `pip`:

```bash
pip install "qrcode[pil]"
```
## Usage 
### 1. Running the Script for Generating Colorful QR Codes Based on Differences in Binary Files
To generate colorful QR codes based on the differences between .bin files, run the following command:

**Command to Run the Script:**
```bash
python binary_to_colorful_qr.py --input_folder "<input_folder_path>" --output_folder "<output_folder_path>" --identifier "<identifier>" --reference_file "/path/to/ref_HBV.fasta"
```

**Arguments:**
* --input_folder: Path to the folder containing .bin files.
* --output_folder: Path to the folder where the generated QR code images will be saved.
* --identifier: An identifier used for naming the output files (e.g., "HBV" for Hepatitis B Virus).
* --reference_file: An identifier for the reference genome sequence from previous run on ```pipeline.py```. 

**Example Run: (using elias delta)** 
```bash
python binary_to_colorful_qr.py --input_folder "/Users/iriskwon/CGFinalProject/HBV/elias_delta_HBV_binary_bin" --output_folder "HBV_colorful_qr_codes" --identifier "HBV" --reference_file "/Users/iriskwon/CGFinalProject/ref_HBV.fasta"
```

## What the script does:
* **Converts the reference FASTA file from `pipeline.py` to binary** and compares each .bin file from the specified binary bin folder against the reference.
* **Generates Colorful QR Codes:** Generates a unique QR code for each file basd on the XOR differences between it and the reference FASTA sequence. 
* **Saves QR Codes:** Generated QR code image is saved with filename indicating the identifier and differences between the files. 

**Example Output:**
```bash
Saved colorful QR code to HBV_colorful_qr_codes/HBV_compressed_HBV_2801893888_vs_compressed_HBV_1519316181.png
```

### 2. Key Components
* **Binary Comparison:** The script compares files byte by byte and creates a byte-by-byte difference (using XOR), which is then encoded in a QR code.
* **Unique Color for Each QR Code:** A unique color is generated for each QR code to visually distinguish between different file comparisons.

#### Additional Notes:
* The script will skip generating a QR code if there are no differences between two files.
* The size and version of the QR code are dynamically adjusted based on the size of the differences.
* The generated QR code images can be scanned using a QR code scanner and decoded to retrieve the differing byte values.


