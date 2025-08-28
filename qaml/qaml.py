from .parser import parse_text
from .templates import load_templates
from .renderer import render

def load_modules(path="modules"):
    """Load template sections from the given modules folder (default: 'modules')."""
    return load_templates(path)

def load_qaml(path, encoding="utf-8"):
    """Parse a .qaml file into an AST."""
    with open(path, "r", encoding=encoding) as f:
        return parse_text(f.read())

def render_html(ast, modules, globals=None):
    """Render an AST to HTML using loaded modules and optional globals for $$VARS."""
    return render(ast, modules, globals=globals) 