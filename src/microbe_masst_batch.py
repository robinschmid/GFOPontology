import sys
import logging
import csv

import microbe_masst as micromasst

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def run_job(usi_or_lib_id, compound_name):
    out_html = "../examples/fast_microbeMasst_{}.html".format(compound_name)

    micromasst.run_microbe_masst(usi_or_lib_id, precursor_mz_tol=0.05, mz_tol=0.02, min_cos=0.7,
                      in_html="collapsible_tree_v3.html", in_ontology="../data/microbe_masst/ncbi.json",
                      metadata_file="../data/microbe_masst/microbe_masst_table.csv",
                      out_counts_file="dist/microbe_masst_counts.tsv",
                      out_json_tree="dist/merged_ncbi_ontology_data.json", format_out_json=True,
                      out_html=out_html, compress_out_html=True, node_key="NCBI", data_key="ncbi"
                      )

if __name__ == '__main__':
    example_link = "https://robinschmid.github.io/GFOPontology/examples/fast_microbeMasst_{}.html"

    jobs = {
        "CCMSLIB00005883671": "GABA",
        "CCMSLIB00006582001": "phe_CA",
        "CCMSLIB00006581985": "glu_CA",
        "CCMSLIB00000006885": "surfactin_C13",
        "CCMSLIB00000006895": "surfactin_C15",
        "CCMSLIB00005721043": "salinosporamide_A",
        "CCMSLIB00006694017": "salinomycin",
        "CCMSLIB00000006871": "actinomycin_d",
        "CCMSLIB00003134958": "actinomycin_d_nist14_match",
        "CCMSLIB00000075066": "arylomycin_a4",
        "CCMSLIB00005772087": "kanamycin_a",
        "CCMSLIB00005464333": "PANTOTHENATE",
        "CCMSLIB00005723628": "acyl_ferrioxamine_2"
    }
    links = []
    for usi_or_lib_id, compound_name in jobs.items():
        run_job(usi_or_lib_id, compound_name)
        links.append((usi_or_lib_id, compound_name, example_link.format(compound_name)))

    sep = "\t"
    header = ["ID", "Compound", "Tree"]
    with open('../examples/example_links.tsv', 'w', newline='', encoding='utf-8') as f:
        write = csv.writer(f)
        write.writerow(header)
        for row in links:
            write.writerow(row)


    sys.exit(0)
