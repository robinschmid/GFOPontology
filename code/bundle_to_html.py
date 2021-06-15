from bs4 import BeautifulSoup
from pathlib import Path
import base64
import requests


def replace_by_local_file(path):
    """
    Replaces web ressources by local files if possible
    :param path: URL
    :return: a local file or the original input string
    """
    if path == "https://d3js.org/d3.v3.min.js":
        return "src/d3.v3.min.js"
    if path == "https://d3js.org/d3.v6.min.js":
        return "src/d3.v6.min.js"
    if path == "https://code.jquery.com/jquery-3.6.0.min.js":
        return "src/jquery-3.6.0.min.js"
    return path


def build_dist_html(input_html, output_html):
    """
    Creates a single distributable HTML file.
    Reads the input_html and internalizes all CSS, JS, and data files into the output html. For web ressources: First
    try to load a local file, else try to download file.
    :param input_html: the input html file that defines all dependencies
    :param output_html: the bundled HTML file
    :return: None
    """
    original_html_text = Path(input_html).read_text(encoding="utf-8")
    soup = BeautifulSoup(original_html_text)

    # Find link tags. example: <link rel="stylesheet" href="css/somestyle.css">
    for tag in soup.find_all('link', href=True):
        if tag.has_attr('href'):
            file_text = Path(tag['href']).read_text(encoding="utf-8")

            # remove the tag from soup
            tag.extract()

            # insert style element
            new_style = soup.new_tag('style')
            new_style.string = file_text
            soup.html.head.append(new_style)

    # Find script tags. example: <script src="js/somescript.js"></script>
    for tag in soup.find_all('script', src=True):
        if tag.has_attr('src'):
            path = tag['src']
            path = replace_by_local_file(path)
            if path.startswith("http"):
                response = requests.get(path)
                response.raise_for_status()
                file_text = response.text
            else:
                file_text = Path(path).read_text()

            # remove the tag from soup
            tag.extract()

            # insert script element
            new_script = soup.new_tag('script')
            new_script.string = file_text
            soup.html.body.append(new_script)

    # Find image tags.
    for tag in soup.find_all('img', src=True):
        if tag.has_attr('src'):
            file_content = Path(tag['src']).read_bytes()

            # replace filename with base64 of the content of the file
            base64_file_content = base64.b64encode(file_content)
            tag['src'] = "data:image/png;base64, {}".format(base64_file_content.decode('ascii'))

    # Save onefile
    with open(output_html, "w", encoding="utf-8") as outfile:
        outfile.write(str(soup))


if __name__ == '__main__':
    build_dist_html("collapsible_tree_v2.html", "dist/oneindex.html")
