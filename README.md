# Kraken-like Taxonomy Parsing Toolkit

A small collection of Python scripts for converting **Kraken2 and Kraken-like taxonomic report files** into taxon-by-sample abundance tables while retaining taxonomic hierarchy.

These scripts were developed to work with Kraken-style output generated from **MMseqs2/GDTB-tk workflows**, but have been designed to also support standard Kraken-like reports using either **full taxonomic rank names** (`genus`, `family`, `species`, etc.) or **single-letter rank codes** (`G`, `F`, `S`, etc.).

The workflow consists of three scripts:

1. `kraken2otu2.py` — generates a taxon-by-sample abundance table at a selected taxonomic rank.
2. `falken_lineage.py` — extracts unique taxonomic lineages from multiple report files.
3. `falken_map.py` — maps the abundance table back onto the taxonomic hierarchy to produce abundance tables with full lineage strings.

---

## Overview

Kraken-style reports contain taxonomic assignments for each sample, but the taxonomic information is generally represented as individual taxonomic ranks.

For example:

```text
Bacteria
Proteobacteria
Gammaproteobacteria
Acidithiobacillales
Acidithiobacillaceae
Acidithiobacillus
Acidithiobacillus ferrooxidans
```

The scripts in this repository allow these reports to be converted into abundance tables while retaining this hierarchical information.

The general workflow is:

```text
Kraken/Kraken-like reports
          │
          ▼
   kraken2otu2.py
          │
          ▼
Taxon × sample abundance table
          │
          │
          ├───────────────┐
          ▼               ▼
falken_lineage.py         │
          │               │
          ▼               │
   lineage database       │
          │               │
          └───────┬───────┘
                  ▼
          falken_map.py
                  │
                  ▼
Abundance table with full
taxonomic lineage strings
```

This is particularly useful when the same taxon name can occur at different points in a taxonomy or when you want to preserve the taxonomic context of each abundance value.

---

# Scripts

## 1. `kraken2otu2.py`

Creates a **taxon-by-sample abundance table** from multiple Kraken/Kraken-like report files.

The user specifies the taxonomic rank to extract.

For example:

```bash
python3 kraken2otu2.py -i ./reports -l genus -e .txt
```

or using the standard single-letter rank code:

```bash
python3 kraken2otu2.py -i ./reports -l G -e .txt
```

Both commands produce:

```text
otu_table_genus.csv
```

The output has the general structure:

```text
otu,sample1,sample2,sample3
Taxon_A,123,456,789
Taxon_B,12,0,45
Taxon_C,0,23,18
```

### Supported taxonomic ranks

The script accepts either full rank names or common single-letter codes:

| Taxonomic rank | Full name      | Code |
| -------------- | -------------- | ---- |
| Superkingdom   | `superkingdom` | `D`  |
| Phylum         | `phylum`       | `P`  |
| Class          | `class`        | `C`  |
| Order          | `order`        | `O`  |
| Family         | `family`       | `F`  |
| Genus          | `genus`        | `G`  |
| Species        | `species`      | `S`  |

For example:

```bash
python3 kraken2otu2.py -i ./reports -l genus -e .txt
```

```bash
python3 kraken2otu2.py -i ./reports -l family -e .txt
```

```bash
python3 kraken2otu2.py -i ./reports -l species -e .txt
```

or:

```bash
python3 kraken2otu2.py -i ./reports -l G -e .txt
```

```bash
python3 kraken2otu2.py -i ./reports -l F -e .txt
```

```bash
python3 kraken2otu2.py -i ./reports -l S -e .txt
```

### Expected report structure

The current script expects a six-column, tab-delimited Kraken-like report where:

* Column 2 = read count
* Column 4 = taxonomic rank
* Column 6 = taxon name

For example:

```text
12.5    1250    0    genus    1234    Acidithiobacillus
5.2     520     0    family   5678    Acidithiobacillaceae
```

The script does not require the taxonomic ranks to be written in full. It can work with either:

```text
genus
family
species
```

or:

```text
G
F
S
```

provided the report structure remains compatible.

---

# 2. `falken_lineage.py`

Extracts the taxonomic hierarchy from multiple Kraken-like report files and creates a unique list of taxonomic lineages.

Example:

```bash
python3 falken_lineage.py \
    -i ./reports \
    -e .txt \
    -o lineages.txt
```

The resulting `lineages.txt` file contains hierarchical taxonomic strings such as:

```text
Bacteria
Bacteria;Proteobacteria
Bacteria;Proteobacteria;Gammaproteobacteria
Bacteria;Proteobacteria;Gammaproteobacteria;Acidithiobacillales
Bacteria;Proteobacteria;Gammaproteobacteria;Acidithiobacillales;Acidithiobacillaceae
Bacteria;Proteobacteria;Gammaproteobacteria;Acidithiobacillales;Acidithiobacillaceae;Acidithiobacillus
```

The script currently recognises the following hierarchy:

```text
superkingdom
    └── phylum
        └── class
            └── order
                └── family
                    └── genus
                        └── species
```

Each unique lineage is written only once.

This creates a simple **taxonomic hierarchy database** that can subsequently be used by `falken_map.py`.

---

# 3. `falken_map.py`

Maps the abundance table produced by `kraken2otu2.py` onto the lineage database produced by `falken_lineage.py`.

For example, `kraken2otu2.py` might produce:

```text
otu,sample1,sample2
Acidithiobacillus,1000,1500
Ferrovum,500,250
Pseudomonas,100,300
```

The lineage file contains:

```text
Bacteria;Proteobacteria;Gammaproteobacteria;Acidithiobacillales;Acidithiobacillaceae;Acidithiobacillus
Bacteria;Proteobacteria;Gammaproteobacteria;Neisseriales;Neisseriaceae;Ferrovum
...
```

`falken_map.py` can then convert the OTU names into their hierarchical taxonomic strings.

For example, a genus-level abundance table can become:

```text
otu,sample1,sample2
Bacteria;Proteobacteria;Gammaproteobacteria;Acidithiobacillales;Acidithiobacillaceae;Acidithiobacillus,1000,1500
Bacteria;Proteobacteria;Gammaproteobacteria;Neisseriales;Neisseriaceae;Ferrovum,500,250
```

This allows the taxonomic context of each taxon to be retained in downstream analyses.

---

# Complete workflow

Assuming your Kraken-like reports are located in:

```text
./reports/
```

## Step 1 — Generate the abundance table

For example, to generate a genus-level table:

```bash
python3 kraken2otu2.py \
    -i ./reports \
    -l genus \
    -e .txt
```

This produces:

```text
./reports/otu_table_genus.csv
```

---

## Step 2 — Generate the lineage database

Run:

```bash
python3 falken_lineage.py \
    -i ./reports \
    -e .txt \
    -o lineages.txt
```

This produces:

```text
lineages.txt
```

The file contains the unique taxonomic hierarchy found across all input reports.

---

## Step 3 — Map the abundance table to the hierarchy

Edit the configuration at the bottom of `falken_map.py`:

```python
abundance_csv = "otu_table_genus.csv"
taxonomy_txt = "lineages.txt"
output_csv = "abundance_with_genus.csv"
desired_level = "genus"
```

Then run:

```bash
python3 falken_map.py
```

The resulting file contains the abundance values together with the corresponding taxonomic hierarchy.

---

# Changing taxonomic resolution

The workflow can be repeated at different taxonomic levels.

For example, for family-level abundance:

```bash
python3 kraken2otu2.py \
    -i ./reports \
    -l family \
    -e .txt
```

Then configure:

```python
abundance_csv = "otu_table_family.csv"
taxonomy_txt = "lineages.txt"
output_csv = "abundance_with_family.csv"
desired_level = "family"
```

Likewise, genus:

```text
-l genus
```

or species:

```text
-l species
```

can be used.

The lineage database can be generated once from a set of reports and then reused for mapping abundance tables at different taxonomic levels.

---

# Input file naming

By default, the scripts look for files ending in:

```text
.txt
```

For example:

```text
sample1_report.txt
sample2_report.txt
sample3_report.txt
```

A different extension can be specified using `-e`:

```bash
python3 kraken2otu2.py -i ./reports -l genus -e .report
```

or:

```bash
python3 falken_lineage.py -i ./reports -e .report
```

The scripts search for files matching:

```text
*<extension>
```

in the specified input directory.

---

# Important assumptions

These scripts are intended for **Kraken-like tab-delimited reports**, rather than arbitrary taxonomy files.

The current implementation assumes:

```text
Column 2 → read count
Column 4 → taxonomic rank
Column 6 → taxon name
```

The taxonomic rank may be represented as either a full name or a single-letter code, depending on the input format.

Before using the scripts on a new type of report, inspect several lines of the input file to confirm that the column structure is compatible.

---

# Why three scripts?

The three scripts deliberately separate the abundance and hierarchy operations.

### `kraken2otu2.py`

Answers:

> **How abundant is each taxon in each sample?**

Output:

```text
taxon × sample
```

### `falken_lineage.py`

Answers:

> **What is the taxonomic hierarchy represented in these reports?**

Output:

```text
taxon hierarchy
```

### `falken_map.py`

Combines the two:

> **What is the abundance of each taxon, while retaining its taxonomic context?**

Output:

```text
full taxonomic lineage × sample
```

This separation means that the same lineage database can be reused for multiple abundance tables.

---

# Origin and acknowledgement

`kraken2otu2.py` was adapted from the `kraken2OTUtable` project by **sipost1**:

**Original repository:**
https://github.com/sipost1/kraken2OTUtable

The original `kraken2otu.py` provided the basis for reading multiple Kraken2 report files and generating taxon-by-sample abundance tables.

`kraken2otu2.py` modifies the original approach to accommodate Kraken-like reports in which taxonomic ranks are provided as full names (e.g. `genus`, `family`, `species`) and extends the rank handling to support both full names and single-letter rank codes.

The `falken_lineage.py` and `falken_map.py` scripts were developed to extend this workflow by extracting and retaining taxonomic hierarchy information across multiple reports.

Please refer to the original repository and its licence for the applicable terms of reuse and redistribution.

---

# Citation

If you use the original `kraken2OTUtable` code or derivatives of it, please acknowledge the original project:

> sipost1. *kraken2OTUtable*. GitHub.
> https://github.com/sipost1/kraken2OTUtable

If you use this toolkit, please also cite the relevant taxonomy software and databases used to generate your input reports (e.g. Kraken2, MMseqs2, GTDB-Tk), as appropriate for your workflow.

---

# Licence

The licensing of the original `kraken2otu.py` code should be respected when redistributing modified versions of that code.

Before publishing this repository, check the licence of the original `kraken2OTUtable` repository and include the appropriate licence file and attribution here.

---

# Status

This is a lightweight research tool developed for parsing Kraken-like taxonomic reports and preparing abundance tables for downstream analysis.

The scripts are intentionally simple and transparent so that they can be readily adapted to other Kraken-like output formats and taxonomic workflows.

```
