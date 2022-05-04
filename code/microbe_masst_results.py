import argparse
import sys
import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def clean_filename(name):
    return name.replace("/peak/", "/ccms_peak/").replace(".mzML", "").replace(".mzXML", "").replace("f.MSV", "MSV")


def create_counts_file(metadata_file, masst_file, out_tsv_file):
    metadata_df = pd.read_csv(metadata_file)
    masst_file = pd.read_csv(masst_file, sep="\t")

    metadata_df["Filepath"] = metadata_df["Filepath"].apply(clean_filename)
    masst_file["filename"] = masst_file["filename"].apply(clean_filename)

    # count matches per ID
    id_matches_dict = dict()

    for index, match_row in masst_file.iterrows():
        # might have multiple rows in the metadata table if multiple IDs
        matching_metadata = metadata_df.loc[metadata_df["Filepath"] == match_row["filename"]]
        for index2, meta_row in matching_metadata.iterrows():
            ncbi_ = meta_row["Taxa_NCBI"]
            id_matches_dict[ncbi_] = id_matches_dict.get(ncbi_, 0) + 1

    df = pd.DataFrame().from_dict(id_matches_dict, orient='index', columns=['matched_size'])
    df.reset_index(inplace=True)
    df = df.rename(columns={'index': 'ncbi'})

    df.to_csv(out_tsv_file, index=False, sep="\t")
    print(df)

if __name__ == '__main__':
    # parsing the arguments (all optional)
    parser = argparse.ArgumentParser(description='Merge MASST results with microbeMASST metadata')
    parser.add_argument('--metadata_file', type=str, help='microbe masst metadata',
                        default="../data/microbe_masst/microbe_masst_table.csv")
    parser.add_argument('--masst_file', type=str, help='a tab separated file with additional data that is added to '
                                                       'metadata file', default="../examples/yersiniabactin.tsv")
    parser.add_argument('--out_tsv_file', type=str, help='output file in .tsv format',
                        default="dist/microbe_masst_counts.tsv")

    args = parser.parse_args()

    # is a url - try to download file
    # something like https://raw.githubusercontent.com/robinschmid/GFOPontology/master/data/GFOP.owl
    # important use raw file on github!
    try:
        create_counts_file(metadata_file=args.metadata_file, masst_file=args.masst_file, out_tsv_file=args.out_tsv_file)
    except Exception as e:
        # exit with error
        logger.exception(e)
        sys.exit(1)

    # exit with OK
    sys.exit(0)
