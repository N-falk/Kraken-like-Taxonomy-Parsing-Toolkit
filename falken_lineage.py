import os
import glob
import argparse

def parse_kraken_taxonomy(file_path):
    with open(file_path, "r") as f:
        lines = [line.rstrip().split("\t") for line in f if line.strip()]

    all_lineages = []

    # Define taxonomic ranks in order
    ranks_order = ['superkingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species']
    rank_to_index = {rank: i for i, rank in enumerate(ranks_order)}
    current_lineage = [""] * len(ranks_order)

    for line in lines:
        if len(line) < 6:
            continue
        rank = line[3].strip().lower()
        name = line[5].strip()

        if rank in rank_to_index:
            idx = rank_to_index[rank]
            current_lineage[idx] = name

            # Clear any deeper ranks
            for j in range(idx + 1, len(current_lineage)):
                current_lineage[j] = ""

            # Add the lineage up to the current level
            lineage = [item for item in current_lineage if item]
            if lineage:
                all_lineages.append(";".join(lineage))

    return all_lineages


def parse_multiple_files(input_dir, extension=".txt", output_file="combined_lineages.txt"):
    all_lineages = []

    files = glob.glob(os.path.join(input_dir, f"*{extension}"))
    if not files:
        raise FileNotFoundError(f"No files with extension {extension} found in {input_dir}")

    print(f"?? Processing {len(files)} files...")

    for file_path in files:
        print(f"  ? {os.path.basename(file_path)}")
        lineages = parse_kraken_taxonomy(file_path)
        all_lineages.extend(lineages)

    unique_lineages = sorted(set(all_lineages))

    with open(output_file, "w") as f:
        for lineage in unique_lineages:
            f.write(lineage + "\n")

    print(f"? Extracted {len(unique_lineages)} unique taxonomic lineages into '{output_file}'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse Kraken reports into taxonomic lineages.")
    parser.add_argument("-i", "--input", type=str, required=True, help="Input directory with Kraken report files")
    parser.add_argument("-e", "--extension", type=str, default=".txt", help="File extension (default: .txt)")
    parser.add_argument("-o", "--output", type=str, default="combined_lineages.txt", help="Output file name")

    args = parser.parse_args()

    parse_multiple_files(args.input, extension=args.extension, output_file=args.output)
