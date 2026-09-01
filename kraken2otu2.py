```python
# -*- coding: utf-8 -*-
"""
Kraken-like report summarizer.

Creates an abundance table at a specified taxonomic rank from multiple
Kraken/Kraken-like report files.

Supports both:
    Full rank names: superkingdom, phylum, class, order, family, genus, species
    Single-letter codes: D, P, C, O, F, G, S

The script is designed to work with Kraken2-style reports as well as
Kraken-like reports where the taxonomic rank names are written in full.
"""

import os
import glob
import csv
import argparse
from collections import defaultdict
from typing import Dict, TextIO


# ---------------------------------------------------------------------
# Command-line arguments
# ---------------------------------------------------------------------

parser = argparse.ArgumentParser(
    description="Create a taxon-by-sample abundance table from Kraken-like reports."
)

parser.add_argument(
    "--inputfolder", "-i",
    type=str,
    required=True,
    help="Input folder containing Kraken-like report files."
)

parser.add_argument(
    "--level", "-l",
    type=str,
    required=True,
    help=(
        "Taxonomic rank to extract. "
        "Can be a full name (e.g. genus, family, species) "
        "or a single-letter code (e.g. G, F, S)."
    )
)

parser.add_argument(
    "--extension", "-e",
    default=".txt",
    help="Extension of report files. Default: .txt"
)

args = parser.parse_args()


# ---------------------------------------------------------------------
# Taxonomic rank aliases
# ---------------------------------------------------------------------

RANK_ALIASES = {
    "d": "superkingdom",
    "domain": "superkingdom",
    "superkingdom": "superkingdom",

    "p": "phylum",
    "phylum": "phylum",

    "c": "class",
    "class": "class",

    "o": "order",
    "order": "order",

    "f": "family",
    "family": "family",

    "g": "genus",
    "genus": "genus",

    "s": "species",
    "species": "species",
}


def normalise_rank(rank: str) -> str:
    """
    Convert a taxonomic rank or rank code into a standard rank name.

    Examples
    --------
    G -> genus
    genus -> genus
    F -> family
    family -> family
    S -> species
    species -> species
    """

    rank = rank.strip().lower()

    if rank not in RANK_ALIASES:
        valid = (
            "superkingdom/D, phylum/P, class/C, order/O, "
            "family/F, genus/G, species/S"
        )
        raise ValueError(
            f"Unknown taxonomic rank '{rank}'. "
            f"Use one of: {valid}"
        )

    return RANK_ALIASES[rank]


# ---------------------------------------------------------------------
# Read a single report
# ---------------------------------------------------------------------

def extract(file: str) -> Dict:
    """
    Parse a Kraken-like report file.

    Returns
    -------
    Dict
        Dictionary containing taxa grouped by taxonomic rank.

    The script expects:
        Column 2 = read count
        Column 4 = taxonomic rank
        Column 6 = taxon name
    """

    taxons = defaultdict(dict)

    with open(file, "r") as ori:
        lines = ori.readlines()

    if not lines:
        raise ValueError(f"{file} is empty!")

    print(f"Reading {file}")

    for line in lines:

        line_params = line.rstrip("\n").split("\t")

        if len(line_params) < 6:
            continue

        read_count = line_params[1].strip()
        rank = line_params[3].strip().lower()
        name = line_params[5].strip()

        taxons[rank][name] = read_count

    return taxons


# ---------------------------------------------------------------------
# Read all report files
# ---------------------------------------------------------------------

def read_in_files(directory: str, extension=args.extension) -> Dict:
    """
    Read all report files in a directory.

    Files are selected based on the supplied extension.
    """

    file_dictionary = defaultdict()

    report_files = glob.glob(f"{directory}/*{extension}")

    if not report_files:
        raise FileNotFoundError(
            "No report file found. "
            "Check the filename extension and input directory."
        )

    print(f"Found {len(report_files)} report files.")

    for file in report_files:

        abs_file = os.path.abspath(file)

        sample_name = os.path.basename(file).replace(extension, "")

        file_dictionary[sample_name] = extract(abs_file)

    return file_dictionary


# ---------------------------------------------------------------------
# Create OTU table
# ---------------------------------------------------------------------

def create_otu_table(
    rank: str,
    file_sample_dict: Dict,
    outdir="./"
) -> TextIO:
    """
    Create an OTU/taxon abundance table for a specified taxonomic rank.

    The rank can be supplied as either a full name or a single-letter code.

    Examples
    --------
    genus
    G

    family
    F

    species
    S
    """

    # Convert G -> genus, F -> family, etc.
    rank = normalise_rank(rank)

    rearranged_dict = defaultdict(dict)

    sample_taxa = {
        sample: ranks.get(rank, {})
        for sample, ranks in file_sample_dict.items()
    }

    for sample, taxon_counts in sample_taxa.items():

        for taxon, count in taxon_counts.items():

            rearranged_dict[taxon][sample] = count

    headers = ["otu"] + list(sample_taxa.keys())

    outfile_name = f"otu_table_{rank}.csv"

    with open(
        os.path.join(outdir, outfile_name),
        "w",
        newline=""
    ) as csv_file:

        writer = csv.writer(csv_file)

        # Write column headers
        writer.writerow(headers)

        # Write abundance values
        for otu, inner_dict in rearranged_dict.items():

            row = [otu]

            for sample in headers[1:]:

                row.append(
                    inner_dict.get(sample, 0)
                )

            writer.writerow(row)


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

if __name__ == "__main__":

    file_dict = read_in_files(args.inputfolder)

    create_otu_table(
        args.level,
        file_dict,
        outdir=args.inputfolder
    )

    print("Done!")
```
