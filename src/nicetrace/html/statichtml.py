from nicetrace import TracingNode
import os

from ..writer.filewriter import write_file
from .staticfiles import get_current_js_and_css_filenames

CDN_VERSION = "22b384eccbf28d3df7ffe008efeb871c066d3811"
CDN_URL = f"https://cdn.jsdelivr.net/gh/spirali/nicetrace@{CDN_VERSION}/src/nicetrace/html/static/"

HTML_TEMPLATE = """<!doctype html>
<html lang="en">

<head>
  <meta charset="UTF-8" />
  <link rel="icon" type="image/svg+xml" href="{url_icon}" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Trace view</title>
  <script>
    function start() {{
       var node = {node_json};
       window.mountTraceView(document.getElementById("root"), node)
    }}
  </script>
  <script type="module" crossorigin src="{url_js}"></script>
  <link rel="stylesheet" crossorigin href="{url_css}">
</head>

<body onload="start()">
  <div id="root"></div>
</body>

</html>"""


def get_static_cdn_html(node_json) -> str:
    js_path, css_path = get_current_js_and_css_filenames()
    url_js = CDN_URL + js_path
    url_css = CDN_URL + css_path
    url_icon = CDN_URL + "icon.svg"
    return HTML_TEMPLATE.format(
        node_json=node_json, url_js=url_js, url_css=url_css, url_icon=url_icon
    )


def get_html(node: TracingNode) -> str:
    return get_static_cdn_html(node.to_dict())


def write_html(node: TracingNode, filename: str | os.PathLike):
    write_file(filename, get_html(node))
