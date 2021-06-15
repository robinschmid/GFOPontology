import argparse
import os
import sys
import requests
from anytree import Node, RenderTree
from anytree.exporter import JsonExporter
import pandas as pd
import json
import numpy as np


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)


def add_data_to_node(node, df, node_field, data_field):
    """
    Merge data into node and apply to all children
    :param node: the current node in a tree structure with ["children"] property
    :param df: the data frame with additional data
    :param node_field: node[field] determines the key to align tree and additional data
    :param data_field: data[field] determines the key to align tree and additional data
    """
    try:
        rowi = df[df[data_field] == node[node_field]].index[0]
        if rowi >= 0:
            for col, value in df.iteritems():
                if col != data_field:
                    # print("%s is %s" % (col, value[rowi]))
                    node[col] = value[rowi]
    except Exception as ex:
        print(ex)
    # apply to all children
    if "children" in node:
        for child in node["children"]:
            add_data_to_node(child, df, node_field, data_field)


def add_data_to_ontology_file(output="dist/merged_ontology_data.json", ontology_file="../data/GFOP.json",
                              data_file="../examples/caffeic_acid.tsv", node_field="name", data_field="group_value",
                              format_json_out=False):
    # read owl file and cache all nodes in a dict{name, node}
    with open(ontology_file) as json_file:
        tree = json.load(json_file)

        # read the additional data
        df = pd.read_csv(data_file, sep='\t')

        # print(df)

        # loop over all children
        add_data_to_node(tree, df, node_field, data_field)

        print("Writing to {}".format(output))
        with open(output, "w") as file:
            if format_json_out:
                out_tree = json.dumps(tree, indent=2, cls=NpEncoder)
            else:
                out_tree = json.dumps(tree, cls=NpEncoder)
            print(out_tree, file=file)


if __name__ == '__main__':
    # parsing the arguments (all optional)
    parser = argparse.ArgumentParser(description='Parse an input owl file to a json tree output. Input can be a path '
                                                 'or URL')
    parser.add_argument('--ontology', type=str, help='the json ontology file with children',
                        default="../data/GFOP.json")
    parser.add_argument('--data', type=str, help='a tab separated file with additional data that is added to the '
                                                 'ontology', default="../examples/caffeic_acid.tsv")
    parser.add_argument('--node_field', type=str, help='the field in the ontology to be compare to the field in the '
                                                       'data file', default="name")
    parser.add_argument('--data_field', type=str,
                        help='the field in the data file to be compared to the field in the ontology',
                        default="group_value")
    parser.add_argument('--output', type=str, help='output file', default="dist/merged_ontology_data.json")
    parser.add_argument('--format', type=bool, help='Format the json output False or True',
                        default=False)
    args = parser.parse_args()

    # is a url - try to download file
    # something like https://raw.githubusercontent.com/robinschmid/GFOPontology/master/data/GFOP.owl
    # important use raw file on github!
    try:
        add_data_to_ontology_file(output=args.output, ontology_file=args.ontology, data_file=args.data,
                                  node_field=args.node_field,
                                  data_field=args.data_field, format_json_out = args.format)
    except Exception as e:
        # exit with error
        print(e)
        sys.exit(1)

    # exit with OK
    sys.exit(0)
