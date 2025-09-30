This Python library enables the generation of visualizations that show the peptide coverage, including cleavage information and motif plots.
This documentation is under development.

Sample usage:
```
enrichment_analysis = CleavageEnrichmentAnalysis()

# import peptide file
peptides = read_peptides(peptide_file)
enrichment_analysis.set_peptides(peptides)

# import metadata file
metadata = read_metadata(meta_file)
enrichment_analysis.metadata = metadata

# import protein file
fastadata = read_fasta(fasta_file)
enrichment_analysis.set_fasta(fastadata)

heatmap_data = heatmap_data(peptides, metadata, fastadata, <additional parameters see method description>)
fig = create_heatmap_figure(**heatmap_data, <additional parameters see method description>
fig.show()

barplot_data = barplot_data(peptides, metadata, fastadata, <additional parameters see method description>)
fig = create_bar_figure(**barplot_data, <additional parameters>)
fig.show()
```
