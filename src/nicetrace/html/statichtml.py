from nicetrace import TracingNode
import os
import json
import uuid

from ..writer.filewriter import write_file
from .staticfiles import get_current_js_and_css_filenames

CDN_VERSION = "d91c60c21ae2e7a900a77507b474028185545691"
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

INLINE_HTML_TEMPLATE = """
<div id="{id}"></div>
<script src="{url_js}"></script>
<link rel="stylesheet" href="{url_css}">
<script>
import("{url_js}").then(() => window.mountTraceView(document.getElementById("{id}"), {node_json}));
</script>
"""


def get_static_cdn_html(template, node_json) -> str:
    js_path, css_path = get_current_js_and_css_filenames()
    url_js = CDN_URL + js_path
    url_css = CDN_URL + css_path
    url_icon = CDN_URL + "icon.svg"
    return template.format(
        node_json=node_json, url_js=url_js, url_css=url_css, url_icon=url_icon
    )


def get_full_html(node: TracingNode) -> str:
    node_json = json.dumps(node.to_dict())
    return get_static_cdn_html(HTML_TEMPLATE, node_json)


def write_html(node: TracingNode, filename: str | os.PathLike):
    """Write a `TracingNode` as static HTML file"""
    write_file(filename, get_full_html(node))


def get_inline_html(node: TracingNode) -> str:
    node_json = json.dumps(node.to_dict())
    template = INLINE_HTML_TEMPLATE.replace("{id}", uuid.uuid4().hex)
    return get_static_cdn_html(template, node_json)
