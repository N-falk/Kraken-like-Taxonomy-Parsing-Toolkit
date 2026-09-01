# Kraken-like Taxonomy Parsing Toolkit

A small collection of Python scripts for parsing **Kraken2-style taxonomic report files**, particularly reports that use full taxonomic rank names (e.g. `genus`, `family`, `phylum`) rather than the abbreviated rank codes commonly used by Kraken2 (e.g. `G`, `F`, `P`).

These scripts were originally developed to process **MMseqs2-derived taxonomic reports in Kraken-like format**, but they can be used more generally with compatible Kraken-style taxonomy reports.

The toolkit provides three complementary functions:

1. **Generate a taxon-by-sample abundance table at a specified taxonomic rank**
2. **Build a database of taxonomic lineages from multiple report files**
3. **Map abundance tables back onto full hierarchical taxonomic names**

Together, these scripts make it possible to go from a collection of Kraken-like reports to abundance tables containing detailed, hierarchical taxonomic names.

---

## Workflow

The three scripts are designed to be used sequentially:

```text
Kraken-like report files
        │
        ├──────────────────────┐
        │                      │
        ▼                      ▼
kraken2otu2.py          falken_lineage.py
        │                      │
        ▼                      ▼
otu_table_genus.csv     combined_lineages.txt
        │                      │
        └──────────┬───────────┘
                   ▼
             falken_map.py
                   │
                   ▼
       abundance_with_genus.csv
```

### In brief

**`kraken2otu2.py`**

Extracts abundances for a specified taxonomic rank from multiple Kraken-like reports and creates a taxon-by-sample abundance table.

**`falken_lineage.py`**

Extracts taxonomic hierarchies from the same reports and creates a unique list of taxonomic lineage strings.

**`falken_map.py`**

Uses the abundance table and lineage database to replace taxon names with their full taxonomic hierarchy.

---

# Input format

The scripts expect a tab-delimited Kraken-like report with at least six columns.

The important columns are:

| Column | Description                            |
| ------ | -------------------------------------- |
| 1      | Percentage or other Kraken-style value |
| 2      | Read count                             |
| 3      | Additional value                       |
| 4      | Taxonomic rank                         |
| 5      | Taxonomic ID                           |
| 6      | Taxon name                             |

For example:

```text
12.34	12345	12345	superkingdom	2	Bacteria
10.21	10234	10234	phylum	1239	Firmicutes
8.52	8523	8523	class	91061	Bacilli
5.21	5210	5210	order	1385	Bacillales
3.42	3420	3420	family	909932	Bacillaceae
2.81	2810	2810	genus	1386	Bacillus
1.42	1420	1420	species	1406	Bacillus subtilis
```

The scripts specifically look for the **taxonomic rank in column 4** and the **taxon name in column 6**.

> **Note:** The scripts were originally modified to work with reports where taxonomic ranks are written as full words such as `genus`, `species`, `family`, etc. If your reports use Kraken2's abbreviated rank codes (`G`, `S`, `F`, etc.), the scripts will need to be modified accordingly.

---

# Requirements

The scripts use standard Python libraries plus `pandas` for `falken_map.py`.

Recommended:

```bash
python3 --version
```

Python 3.8+ is recommended.

Install pandas if necessary:

```bash
pip install pandas
```

---

# 1. `kraken2otu2.py`

## What it does

`kraken2otu2.py` reads multiple Kraken-like report files and extracts the abundance of taxa at a specified taxonomic rank.

For example, specifying:

```text
genus
```

will produce a table containing all genera detected across the input samples.

The resulting table has:

* one row per taxon
* one column per sample
* read counts as abundance values

Example:

```text
otu,Bacillus,Escherichia,Ferrovum
Sample1,120,54,12
Sample2,85,91,22
Sample3,102,43,31
```

More generally, the structure is:

```text
otu,sample1,sample2,sample3,...
taxon1,count,count,count,...
taxon2,count,count,count,...
```

## Usage

```bash
python3 kraken2otu2.py -i ./reports -l genus -e .txt
```

Arguments:

| Argument              | Description                                          |
| --------------------- | ---------------------------------------------------- |
| `-i`, `--inputfolder` | Directory containing Kraken-like report files        |
| `-l`, `--level`       | Taxonomic rank to extract                            |
| `-e`, `--extension`   | File extension/pattern used to identify report files |

For example:

```bash
python3 kraken2otu2.py \
    -i ./reports \
    -l genus \
    -e _report
```

This searches for files ending in `_report`.

The output is written to the input directory as:

```text
otu_table_genus.csv
```

For species-level abundance:

```bash
python3 kraken2otu2.py -i ./reports -l species -e _report
```

which produces:

```text
otu_table_species.csv
```

---

# 2. `falken_lineage.py`

## What it does

`falken_lineage.py` extracts taxonomic hierarchies from multiple Kraken-like report files.

Rather than simply recording individual taxa, it reconstructs the hierarchy represented in each report.

For example:

```text
Bacteria
Bacteria;Proteobacteria
Bacteria;Proteobacteria;Gammaproteobacteria
Bacteria;Proteobacteria;Gammaproteobacteria;Acidithiobacillales
Bacteria;Proteobacteria;Gammaproteobacteria;Acidithiobacillales;Acidithiobacillaceae
Bacteria;Proteobacteria;Gammaproteobacteria;Acidithiobacillales;Acidithiobacillaceae;Acidithiobacillus
```

The output is deduplicated, producing a database of unique taxonomic strings observed across all input reports.

This is useful because the same genus name can potentially occur in different taxonomic contexts. The lineage file provides the information needed to associate a taxon with its hierarchical classification.

## Usage

```bash
python3 falken_lineage.py -i ./reports -e _report -o combined_lineages.txt
```

Arguments:

| Argument            | Description                                     |
| ------------------- | ----------------------------------------------- |
| `-i`, `--input`     | Directory containing Kraken-like report files   |
| `-e`, `--extension` | File extension/pattern identifying report files |
| `-o`, `--output`    | Name of the lineage output file                 |

Example:

```bash
python3 falken_lineage.py \
    -i ./reports \
    -e _report \
    -o combined_lineages.txt
```

Output:

```text
combined_lineages.txt
```

---

# 3. `falken_map.py`

## What it does

`falken_map.py` combines the outputs of the first two scripts.

It takes:

1. An abundance table generated by `kraken2otu2.py`
2. A lineage database generated by `falken_lineage.py`

It then replaces the taxon names in the abundance table with their full taxonomic hierarchy.

For example, an abundance table might initially contain:

```text
otu,sample1,sample2,sample3
Bacillus,100,250,80
Ferrovum,50,120,35
```

After mapping, the OTU names can become:

```text
otu,sample1,sample2,sample3
Bacteria;Firmicutes;Bacilli;Bacillales;Bacillaceae;Bacillus,100,250,80
Bacteria;Proteobacteria;Gammaproteobacteria;Burkholderiales;Gallionellaceae;Ferrovum,50,120,35
```

This preserves the abundance values while adding taxonomic context to the taxon names.

## Usage

Unlike the first two scripts, the input/output filenames and desired taxonomic level are currently specified **inside the Python script**.

Edit:

```python
abundance_csv = "otu_table_genus.csv"
taxonomy_txt = "combined_lineages.txt"
output_csv = "abundance_with_genus.csv"
desired_level = "genus"
```

For example:

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

# Complete example workflow

Suppose a directory contains:

```text
reports/
├── sample1_report
├── sample2_report
├── sample3_report
├── sample4_report
└── ...
```

## Step 1 — Generate genus abundance table

```bash
python3 kraken2otu2.py \
    -i ./reports \
    -l genus \
    -e _report
```

This produces:

```text
reports/otu_table_genus.csv
```

---

## Step 2 — Generate the taxonomic lineage database

```bash
python3 falken_lineage.py \
    -i ./reports \
    -e _report \
    -o combined_lineages.txt
```

This produces:

```text
combined_lineages.txt
```

---

## Step 3 — Map genera to their full taxonomy

Edit `falken_map.py`:

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

The final output is:

```text
abundance_with_genus.csv
```

---

# Choosing a taxonomic level

The scripts currently recognise the following taxonomic hierarchy:

```text
superkingdom
phylum
class
order
family
genus
species
```

For example, running `kraken2otu2.py` at the genus level:

```bash
python3 kraken2otu2.py -i ./reports -l genus -e _report
```

followed by `falken_map.py` with:

```python
desired_level = "genus"
```

will produce names such as:

```text
Bacteria;Proteobacteria;Gammaproteobacteria;Burkholderiales;Gallionellaceae;Ferrovum
```

rather than simply:

```text
Ferrovum
```

This can be particularly useful for downstream ecological and microbiome analyses where retaining taxonomic context is important.

---

# Important considerations

### Taxonomic names must be consistent

The mapping performed by `falken_map.py` relies on taxon names matching between the abundance table and lineage database.

If a taxon cannot be found in the lineage database, the original taxon name is retained.

### Use the same report set

The abundance table and lineage database should ideally be generated from the **same collection of report files**.

For example:

```text
reports/
    sample1_report
    sample2_report
    sample3_report
```

should be used to generate both:

```text
otu_table_genus.csv
```

and:

```text
combined_lineages.txt
```

### Database/version consistency

If the Kraken-like reports were generated using different taxonomic databases or database versions, taxonomic names and classifications may not be directly comparable.

For reproducible analyses, it is recommended that reports being combined were generated using the same taxonomy database/version and comparable classification settings.

### Rank naming

These scripts expect full rank names such as:

```text
superkingdom
phylum
class
order
family
genus
species
```

They do not automatically translate abbreviated Kraken2 rank codes such as:

```text
D
P
C
O
F
G
S
```

---

# Why three scripts?

The separation into three scripts provides flexibility.

`kraken2otu2.py` answers:

> **What taxa are present, and how abundant are they in each sample?**

`falken_lineage.py` answers:

> **What taxonomic hierarchy is associated with the taxa detected across my dataset?**

`falken_map.py` answers:

> **Can I combine those two pieces of information so that my abundance table retains the full taxonomic hierarchy?**

This separation also means that the same lineage database can potentially be reused for multiple abundance tables generated from the same report collection.

---

# Original application

These scripts were initially developed for processing MMseqs2-derived taxonomic assignments generated in a Kraken-like report format.

The original workflow involved:

```text
MMseqs2 taxonomic assignment
            ↓
Kraken-like reports
            ↓
kraken2otu2.py
            ↓
taxon abundance table
            +
falken_lineage.py
            ↓
taxonomic lineage database
            ↓
falken_map.py
            ↓
hierarchical abundance table
```

The scripts themselves do not require MMseqs2 and are intended to be useful for other Kraken-like report formats that follow the expected tab-delimited structure.

---

# Citation / acknowledgement

If you use these scripts in published work, please cite the original taxonomic classification software/database used to generate your reports (e.g. Kraken2, MMseqs2, GTDB, or another relevant resource), in addition to citing this repository where appropriate.

---

# License

[Add your preferred license here, e.g. MIT License.]

---

# Contributing

Issues, suggestions, bug reports, and pull requests are welcome.

If you encounter a Kraken-like report format that is not handled correctly, please provide an example of the report structure (with any sensitive information removed) when opening an issue.
