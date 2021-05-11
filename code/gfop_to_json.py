import argparse
import os
import sys
import requests
from anytree import Node, RenderTree
from anytree.exporter import JsonExporter
from pronto import Ontology


# this script was tested on .owl --> .json
# it somehow failed on .obo --> .json
# from https://webprotege.stanford.edu/ choose download as RDF/XML

def convert_to_json(input="GFOP.owl", output="GFOP.json"):
    # create a root to bundle everything
    root: Node = Node("GFOP")
    nodes = {}

    # read owl file and cache all nodes in a dict{name, node}
    obo = Ontology(input)
    for term in obo.terms():
        id = term.id
        name = term.name
        # find parents in distance 1 (exclude self)
        parent_terms = term.superclasses(with_self=False, distance=1).to_set()
        if parent_terms is None or len(parent_terms) == 0:
            # create root node
            nodes[name] = Node(name, id=id)
        else:
            # currently only uses one parent
            parent = parent_terms.pop()
            nodes[name] = Node(name, id=id, parent_id=parent.id, parent_name=parent.name)

    # link all nodes to their parents
    for key, node in nodes.items():
        if key is not root.name:
            try:
                # find parent in cached nodes and set to node
                node.parent = nodes[node.parent_name]
            except AttributeError:
                # no parent - add to root
                node.parent = root

    # generate json string
    exporter = JsonExporter(indent=2, sort_keys=True)
    json = exporter.export(root)

    # print json and tree for debugging
    print(json)

    for pre, _, node in RenderTree(root):
        print("%s%s" % (pre, node.name))

    # export to json file
    print("Writing to {}".format(output))
    with open(output, "w") as file:
        print(json, file=file)


def convert_from_url(url, output, username, password):
    try:
        print("Downloading from {}".format(url))
        if username is None or len(username) == 0:
            response = requests.get(url)
        else:
            response = requests.get(url, auth=(username, password))

        if response.ok:
            temp = os.path.join(os.getcwd(), "temp.txt")
            with open(temp, 'w') as f:
                f.write(response.text)

            convert_to_json(input=temp, output=output)
            os.remove(temp)
        else:
            raise AttributeError("Get failed. Response: {} from {}".format(response.status_code, url))
    except:
        print("Error while getting file from url {}".format(url))
        raise


if __name__ == '__main__':
    # parsing the arguments (all optional)
    parser = argparse.ArgumentParser(description='Parse an input owl file to a json tree output. Input can be a path '
                                                 'or URL')
    parser.add_argument('--input', type=str, help='input file', default="GFOP.owl")
    parser.add_argument('--output', type=str, help='output file', default="GFOP.json")
    parser.add_argument('--username', type=str, help='username for authentication if a url was passed to input',
                        default="")
    parser.add_argument('--password', type=str, help='password for authentication if a url was passed to input',
                        default="")
    args = parser.parse_args()

    # is a url - try to download file
    # something like https://raw.githubusercontent.com/robinschmid/GFOPontology/master/data/GFOP.owl
    # important use raw file on github!
    try:
        if args.input.startswith("http"):
            convert_from_url(url=args.input, output=args.output, username=args.username, password=args.password)
        else:
            convert_to_json(input=args.input, output=args.output)
    except Exception as e:
        # exit with error
        print(e)
        sys.exit(1)

    # exit with OK
    sys.exit(0)
