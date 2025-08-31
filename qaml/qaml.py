import os
from .parser import parse_qaml
from .renderer import render
from .template import parse_templates


def load_templates(path="templates", encoding="utf-8"):
    """
    Load all template files in a folder.
    Each file may contain multiple [BLOCK]... definitions.
    Returns a dict {name: Template}.
    """
    templates = {}
    for fname in os.listdir(path):
        if not fname.lower().endswith((".html", ".t")):
            continue
        fpath = os.path.join(path, fname)
        with open(fpath, "r", encoding=encoding) as f:
            text = f.read()
        parsed = parse_templates(text)
        templates.update(parsed)
    return templates


def load_qaml(path, encoding="utf-8"):
    """
    Parse a .qaml file into an AST root node.
    """
    with open(path, "r", encoding=encoding) as f:
        return parse_qaml(f.read())


def render_html(ast, templates, values=None):
    """
    Render an AST to HTML using loaded templates and optional global vars.
    """
    return render(ast, templates, values=values)
