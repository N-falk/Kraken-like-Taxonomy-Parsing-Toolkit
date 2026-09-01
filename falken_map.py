import pandas as pd

def load_hierarchy_database(hierarchy_file):
    """Load hierarchy text file into a dictionary mapping taxon names to their full lineages."""
    taxon_to_lineage = {}
    with open(hierarchy_file, 'r') as f:
        for line in f:
            lineage = line.strip().split(";")
            for i, name in enumerate(lineage):
                name = name.strip()
                if name:  # avoid empty strings
                    taxon_to_lineage[name] = lineage[:i+1]
    return taxon_to_lineage


def map_taxa_to_lineages(abundance_file, taxonomy_file, output_file, max_level):
    # Load abundance CSV
    df = pd.read_csv(abundance_file)

    # Load hierarchy database
    taxon_to_lineage = load_hierarchy_database(taxonomy_file)

    # Define taxonomy rank order
    ranks_order = ['superkingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species']
    if max_level not in ranks_order:
        raise ValueError(f"Invalid taxonomic level: {max_level}. Choose from: {ranks_order}")

    max_index = ranks_order.index(max_level)

    # Replace OTU names with hierarchy up to specified level
    new_otus = []
    for otu in df['otu']:
        lineage = taxon_to_lineage.get(otu)
        if lineage:
            # Pad lineage if needed
            lineage_extended = lineage + [''] * (len(ranks_order) - len(lineage))
            truncated = lineage_extended[:max_index+1]
            new_otus.append(";".join(truncated))
        else:
            # Fallback if no lineage is found
            new_otus.append(otu)

    df['otu'] = new_otus
    df.to_csv(output_file, index=False)
    print(f"? Output written to: {output_file}")


# Example usage
if __name__ == "__main__":
    abundance_csv = "otu_table_species.csv"        # Your abundance table
    taxonomy_txt = "lineages.txt"         # Your full taxonomy lineage file
    output_csv = "abundance_with_species.csv"
    desired_level = "species"               # Change to genus, species, etc. as needed

    map_taxa_to_lineages(abundance_csv, taxonomy_txt, output_csv, desired_level)
