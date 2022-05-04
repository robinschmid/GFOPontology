import argparse
import os
import sys
import requests
from anytree import Node, RenderTree
from anytree.exporter import JsonExporter


def convert_to_json(input="canopus_classyfire/classyfire.json", output="canopus_classyfire/classyfire_ontology.json"):
    import json
    # create a root to bundle everything
    root: Node
    nodes = {}

    # read owl file and cache all nodes in a dict{name, node}
    with open(input) as json_file:
        data = json.load(json_file)
        for term in data:
            id = term["chemont_id"]
            name = term["name"]
            parent_id = term["parent_chemont_id"]

            if parent_id == None or parent_id == "null":
                # create root node
                root = Node(name, id=id)
                nodes[id] = root
            else:
                # currently only uses one parent
                nodes[id] = Node(name, id=id, parent_id=parent_id)

        # link all nodes to their parents
        for key, node in nodes.items():
            if key is not root.id:
                try:
                    # find parent in cached nodes and set to node
                    node.parent = nodes[node.parent_id]
                except AttributeError as ex:
                    print(ex)
                    raise ex


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
    parser.add_argument('--input', type=str, help='input file', default="canopus_classyfire/classyfire.json")
    parser.add_argument('--output', type=str, help='output file', default="canopus_classyfire/classyfire_ontology.json")
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
