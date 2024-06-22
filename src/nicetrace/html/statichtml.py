CDN_VERSION = "9fbc2169cd64cac537b74c432a6d1a7a2b7e8b0c"
CDN_URL = (
    f"https://cdn.jsdelivr.net/gh/spirali/nicetrace@{CDN_VERSION}/src/nicetrace/static/"
)

HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <link rel="icon" type="image/svg+xml" href="/vite.svg" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>NiceTrace</title>
  <script type="module" crossorigin src="{js_path}"></script>
  <link rel="stylesheet" crossorigin href="{css_path}">
  <script>
    function start() {{
      var node = {node};
      window.mountTraceView(document.getElementById("root"), node)
    }}
  </script>
</head>

<body onload="start()">
  <div id="root"></div>
</body>
</html>
"""


def get_static_html(node_json, html_files):
    js_path, css_path = html_files
    return HTML_TEMPLATE.format(node=node_json, js_path=js_path, css_path=css_path)
