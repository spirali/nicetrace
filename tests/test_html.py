from nicetrace import trace, write_html
import requests


def extract(s, start, end):
    s1 = s.index(start)
    s1 += len(start)
    s2 = s.index(end, s1)
    return s[s1:s2]


def test_cdn_html(tmp_path):
    with trace("Root") as root:
        with trace("Child1", inputs={"x": 1}):
            pass

    target = tmp_path / "out.html"
    print(target)
    write_html(root, target)

    with open(target, "r") as f:
        data = f.read()

    assert "Child1" in data

    url_js = extract(data, '<script type="module" crossorigin src="', '"></script>')
    url_css = extract(data, '<link rel="stylesheet" crossorigin href="', '">')

    r = requests.get(url_js)
    assert r.status_code == 200
    r = requests.get(url_css)
    assert r.status_code == 200
