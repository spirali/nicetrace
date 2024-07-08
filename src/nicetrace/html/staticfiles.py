import importlib.resources as resources
import os

from . import static

STATIC_FILE_DIR = os.path.dirname(resources.files(static) / "x")
STATIC_FILES = [str(path) for path in resources.files(static).iterdir()]


def read_index():
    with (resources.files(static) / "index.html").open("r") as f:
        return f.read()


def get_current_js_and_css_filenames():
    js = [
        os.path.basename(filename)
        for filename in STATIC_FILES
        if filename.endswith(".js")
    ]
    assert len(js) == 1
    css = [
        os.path.basename(filename)
        for filename in STATIC_FILES
        if filename.endswith(".css")
    ]
    assert len(css) == 1
    return js[0], css[0]


# def copy_static_files(target_path: str):
#     js_path, css_path = get_current_js_and_css_filenames()
#     js = os.path.basename(js_path)
#     css = os.path.basename(css_path)
#
#     target_js = os.path.join(target_path, js)
#     target_css = os.path.join(target_path, css)
#
#     if not os.path.exists(target_js):
#         shutil.copyfile(js_path, target_js)
#     if not os.path.exists(target_css):
#         shutil.copyfile(css_path, target_css)
#     return js, css
