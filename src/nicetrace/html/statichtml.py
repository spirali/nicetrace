HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <link rel="icon" type="image/svg+xml" href="/vite.svg" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Vite + React + TS</title>
  <script>
    function start() {{
      var node = {node};
      window.mountTraceView(document.getElementById("root"), node)
    }}
  </script>
  <script type="module" crossorigin src="{js_path}"></script>
  <link rel="stylesheet" crossorigin href="{css_path}">
</head>

<body onload="start()">
  <div id="root"></div>
</body>
</html>
"""


def get_static_html(node_json, html_files):
    js_path, css_path = html_files
    return HTML_TEMPLATE.format(node=node_json, js_path=js_path, css_path=css_path)
