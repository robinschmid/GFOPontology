# GFOPontology

## Update ontology
### GFOP
In case of an update to the GFOP ontology, replace the _data/GFOP.owl_ file (download from webprotege as RDF/XML) and run the _gfop_to_json.py_ script. This will create a json tree of the ontology.

### Classyfire
Download the classyfire ontology in json format. Run the _classyfire_to_json_ontology.py_ script to generate the correct format for the tree.

## Build ontology tree
Run the build_tree.py script to create a single html file that contains the javascript tree, data, and html page. 
This will:
1. Input: Ontology (json), extra data (tsv), html page with dependencies
2. Output: Merged tree data (json), self-contained html page (single file)
3. Merges extra data (e.g., MASST results) from a tsv-file (tab-separated) into an ontology tree (optional)
4. Uses base html file to internalize the tree data and all dependencies
5. Find the resulting tree data file and html file in the _dist_ folder. Default: _dist/oneindex.html_

