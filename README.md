# Parsing Kraken-like Taxonomic Reports

A small collection of Python scripts for processing **Kraken-like taxonomic report files** and generating taxon-by-sample abundance tables with taxonomic hierarchy preserved.

These scripts were developed to process taxonomic output generated from **MMseqs2/GDTB-tk workflows** that uses a format similar to Kraken2 reports, but represents taxonomic ranks using their full names (e.g. `phylum`, `family`, `genus`, `species`) rather than the abbreviated rank codes used by Kraken2.

The workflow can:

1. Extract taxon abundances from multiple report files at a specified taxonomic rank.
2. Generate a database of taxonomic lineages represented across all samples.
3. Map abundance data back onto full taxonomic lineage strings.

The resulting tables can therefore retain information about the **taxonomic hierarchy** while maintaining a conventional taxon-by-sample abundance format.

---

## Workflow

The three scripts are intended to be used sequentially:

```text
Kraken-like report files
        │
        ├──────────────────────────────┐
        │                              │
        ▼                              ▼
kraken2otu2.py                  falken_lineage.py
        │                              │
        ▼                              ▼
Taxon abundance table           Taxonomic lineage database
        │                              │
        └──────────────┬───────────────┘
                       ▼
                falken_map.py
                       │
                       ▼
        Hierarchical abundance table
```

For example, starting with multiple Kraken-like report files:

```text
sample1_report.txt
sample2_report.txt
sample3_report.txt
...
```

the workflow can produce:

```text
otu_table_genus.csv
combined_lineages.txt
abundance_with_genus.csv
```

where the final abundance table contains taxonomic names such as:

```text
Bacteria;Proteobacteria;Gammaproteobacteria;Pseudomonadales;Pseudomonadaceae;Pseudomonas
```

rather than simply:

```text
Pseudomonas
```

---

# Scripts

## 1. `kraken2otu2.py`

Creates a taxon-by-sample abundance table from multiple Kraken-like report files.

The script extracts the read count associated with each taxon at a specified taxonomic rank and combines the results across all input samples.

Unlike the original `kraken2otu.py` script on which this was based, this version is designed for reports where taxonomic ranks are represented by their **full names**, for example:

```text
superkingdom
phylum
class
order
family
genus
species
```

rather than abbreviated Kraken2 rank codes such as:

```text
D
P
C
O
F
G
S
```

### Usage

```bash
python3 kraken2otu2.py -i ./reports -l genus -e .txt
```

Arguments:

| Argument              | Description                                                  |
| --------------------- | ------------------------------------------------------------ |
| `-i`, `--inputfolder` | Directory containing the report files                        |
| `-l`, `--level`       | Taxonomic rank to extract, e.g. `genus`, `species`, `family` |
| `-e`, `--extension`   | Extension of input files; default is `.txt`                  |

The output is written to the input directory as:

```text
otu_table_genus.csv
```

for a genus-level analysis.

The rows represent taxa and the columns represent samples.

Example:

```text
otu,sample1,sample2,sample3
Pseudomonas,32447,67432,12543
Acinetobacter,16974,16974,1832
Shewanella,24114,24114,532
```

---

## 2. `falken_lineage.py`

Generates a list of the taxonomic lineages represented across all input report files.

The script reads the taxonomic hierarchy contained within the reports and reconstructs lineage strings from:

```text
superkingdom
phylum
class
order
family
genus
species
```

For example, instead of simply recording:

```text
Pseudomonas
```

it can generate:

```text
Bacteria;Proteobacteria;Gammaproteobacteria;Pseudomonadales;Pseudomonadaceae;Pseudomonas
```

The resulting file contains unique lineage strings and acts as a simple taxonomy hierarchy database for the subsequent mapping step.

### Usage

```bash
python3 falken_lineage.py -i ./reports -e .txt -o combined_lineages.txt
```

Arguments:

| Argument            | Description                                 |
| ------------------- | ------------------------------------------- |
| `-i`, `--input`     | Directory containing the report files       |
| `-e`, `--extension` | Extension of input files; default is `.txt` |
| `-o`, `--output`    | Name of the output lineage file             |

Example output:

```text
Bacteria
Bacteria;Proteobacteria
Bacteria;Proteobacteria;Gammaproteobacteria
Bacteria;Proteobacteria;Gammaproteobacteria;Pseudomonadales
Bacteria;Proteobacteria;Gammaproteobacteria;Pseudomonadales;Pseudomonadaceae
Bacteria;Proteobacteria;Gammaproteobacteria;Pseudomonadales;Pseudomonadaceae;Pseudomonas
```

---

## 3. `falken_map.py`

Maps the abundance table produced by `kraken2otu2.py` onto the lineage database produced by `falken_lineage.py`.

This allows taxon names in the abundance table to be replaced with their full taxonomic hierarchy.

For example:

```text
Pseudomonas
```

can become:

```text
Bacteria;Proteobacteria;Gammaproteobacteria;Pseudomonadales;Pseudomonadaceae;Pseudomonas
```

The script can truncate the hierarchy at a desired taxonomic level.

For example, a genus-level output would retain:

```text
Bacteria;Proteobacteria;Gammaproteobacteria;Pseudomonadales;Pseudomonadaceae;Pseudomonas
```

while a family-level output would retain:

```text
Bacteria;Proteobacteria;Gammaproteobacteria;Pseudomonadales;Pseudomonadaceae
```

### Usage

The input and desired taxonomic level are currently specified within the script:

```python
abundance_csv = "otu_table_genus.csv"
taxonomy_txt = "combined_lineages.txt"
output_csv = "abundance_with_genus.csv"
desired_level = "genus"
```

Then run:

```bash
python3 falken_map.py
```

---

# Complete Example

Assume a directory contains:

```text
reports/
├── sample1_report.txt
├── sample2_report.txt
├── sample3_report.txt
└── sample4_report.txt
```

### Step 1 — Generate the abundance table

For genus-level abundances:

```bash
python3 kraken2otu2.py \
    -i ./reports \
    -l genus \
    -e .txt
```

This creates:

```text
reports/otu_table_genus.csv
```

---

### Step 2 — Generate the lineage database

```bash
python3 falken_lineage.py \
    -i ./reports \
    -e .txt \
    -o combined_lineages.txt
```

This creates:

```text
combined_lineages.txt
```

containing the unique taxonomic lineages represented across the input reports.

---

### Step 3 — Add hierarchical taxonomy to the abundance table

Edit the settings at the bottom of `falken_map.py`:

```python
abundance_csv = "otu_table_genus.csv"
taxonomy_txt = "combined_lineages.txt"
output_csv = "abundance_with_genus.csv"
desired_level = "genus"
```

Then:

```bash
python3 falken_map.py
```

The resulting file:

```text
abundance_with_genus.csv
```

contains the original abundance information but with the taxon names replaced by hierarchical lineage strings.

---

# Supported Taxonomic Levels

The scripts currently recognise the following ranks:

```text
superkingdom
phylum
class
order
family
genus
species
```

For example:

```bash
python3 kraken2otu2.py -i ./reports -l genus -e .txt
```

or:

```bash
python3 kraken2otu2.py -i ./reports -l family -e .txt
```

or:

```bash
python3 kraken2otu2.py -i ./reports -l species -e .txt
```

---

# Input Format

The scripts are designed for **Kraken-like tab-delimited taxonomic reports** containing at least six fields, with the relevant information in the following positions:

```text
field 2 → read count
field 4 → taxonomic rank
field 6 → taxon name
```

For example:

```text
27.67    168354    0    superkingdom    2    Bacteria
23.46    142758    1804    phylum    1224    Proteobacteria
17.38    105738    1070    class    1236    Gammaproteobacteria
8.18     49747     24      order    72274   Pseudomonadales
5.35     32566     36      family   135621  Pseudomonadaceae
5.33     32447     4268    genus    286     Pseudomonas
```

The exact upstream software producing these reports may vary; the important requirement is that the reports follow this general tab-delimited structure.

---

# Relationship to Kraken2

These scripts are **not a replacement for Kraken2** and do not perform taxonomic classification themselves.

Instead, they are designed to parse **Kraken-like report files that have already been generated by a taxonomic classification workflow**.

They may therefore be useful for outputs from other tools or pipelines that produce a report structure similar to Kraken2.

---

# Acknowledgements and Original Code

The `kraken2otu2.py` script was adapted from [`kraken2otu.py`](https://github.com/sipost1/kraken2OTUtable) by **sipost1**.

The original `kraken2otu.py` creates a simple taxon-by-sample OTU table from Kraken2 reports. The original repository describes the script as extracting taxon names and read counts from multiple Kraken2 report files and combining them into a single OTU table.

`kraken2otu2.py` retains the core approach of the original script but has been modified to:

* process Kraken-like reports using full taxonomic rank names;
* support ranks such as `genus`, `family`, and `species`;
* handle malformed/incomplete report lines;
* accommodate the report format generated by the upstream MMseqs2/GDTB-tk workflow.

The additional scripts, `falken_lineage.py` and `falken_map.py`, were developed to extend this approach by generating and applying hierarchical taxonomic lineage information.

Original repository:

https://github.com/sipost1/kraken2OTUtable

The original repository is distributed under the **MIT License**.

---

# Licence

This project contains modified code derived from `kraken2otu.py` from the `sipost1/kraken2OTUtable` repository.

The original code is distributed under the MIT License. Please see the accompanying `LICENSE` file for the applicable licence terms and attribution.

---

# Notes

These scripts were developed primarily for processing microbial metagenomic taxonomic data and are intended to provide a lightweight way of converting Kraken-like report files into abundance tables suitable for downstream analysis in R, Python, or other statistical environments.

The scripts are deliberately simple and do not attempt to perform extensive validation of taxonomy or resolve conflicting taxonomic assignments between reports. Users should therefore inspect their input reports and confirm that the taxonomic format is consistent across samples before combining them.
