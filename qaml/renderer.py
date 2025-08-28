import html, re
from .block import Block

# --- escaping ---
def _esc(s):
    return html.escape(s, quote=True)

# --- attribute exposure helpers ---
SAFE_ATTR_PREFIXES = ("data-", "aria-")
SAFE_ATTRS = {
    "id","class","style","title","alt","src","href","width","height",
    "role","type","name","value","for","placeholder","rel","target"
}

def _expose_all(props):
    parts = []
    for k, v in props.items():
        kl = k.lower()
        if kl in SAFE_ATTRS or any(kl.startswith(p) for p in SAFE_ATTR_PREFIXES):
            parts.append(f'{k}="{_esc(str(v))}"')
    return " ".join(parts)

# --- template token regexes ---
RE_EXPOSE = re.compile(r"\$EXPOSE\s+([A-Za-z_:][-A-Za-z0-9_:.]*)")
RE_EXPOSE_AS = re.compile(r"\$EXPOSE_AS\s+([A-Za-z_][\w:-]*)\s*->\s*([A-Za-z_:][-A-Za-z0-9_:.]*)")
RE_GLOBAL = re.compile(r"\$\$([A-Za-z_][A-Za-z0-9_]*)")

def render(block, templates, globals=None):
    """Render AST to HTML string using *templates* dict.
    Accepts optional *globals* dict for $$VARS in templates.
    """
    return _render_node(block, templates, globals or {})

def _render_node(node, templates, gvars):
    if isinstance(node, str):
        return _esc(node)

    if isinstance(node, Block):
        # Special root handling
        if node.name == "__ROOT__":
            # If user provided an explicit ROOT block, render normally
            has_root = any(isinstance(ch, Block) and ch.name == "ROOT" for ch in node.children)
            if has_root or "ROOT" not in templates:
                return "".join(_render_node(ch, templates, gvars) for ch in node.children)
            # Otherwise, auto-wrap with ROOT template
            synthetic_root = Block("ROOT")
            synthetic_root.children = node.children[:]  # share references; rendering is read-only
            # Title propagation happens inside template replacement via _title_of
            return _render_block(synthetic_root, templates, gvars)

        # Regular block
        return _render_block(node, templates, gvars)

    raise TypeError(f"Unknown node: {node!r}")

def _render_block(block, templates, gvars):
    body = "".join(_render_node(ch, templates, gvars) for ch in block.children)
    tpl = templates.get(block.name)
    if not tpl:
        # fallback: debug wrapper
        return f'<div data-qaml="{block.name}">{body}</div>'

    # Compute title with new precedence
    title = _title_of(block, gvars)

    # First replace $$GLOBALS (can appear anywhere)
    out = RE_GLOBAL.sub(lambda m: _esc(str(gvars.get(m.group(1), ""))), tpl)

    # Replace standard placeholders that don't require scanning order
    out = (out
           .replace("$BODY", body)
           .replace("$EXPOSE_ALL", _expose_all(block.props))
           .replace("$TITLE", _esc("" if title is None else title)))

    # Replace targeted $EXPOSE <attr>
    def _rep_expose(m):
        attr = m.group(1)
        if attr in block.props:
            return f'{attr}="{_esc(str(block.props[attr]))}"'
        return ""

    out = RE_EXPOSE.sub(_rep_expose, out)

    # Replace $EXPOSE_AS prop -> attr
    def _rep_expose_as(m):
        prop, attr = m.group(1), m.group(2)
        if prop in block.props:
            return f'{attr}="{_esc(str(block.props[prop]))}"'
        return ""

    out = RE_EXPOSE_AS.sub(_rep_expose_as, out)

    return out

def _title_of(block, gvars):
    # 1) If this block is ROOT and has .title
    if block.name == "ROOT" and "title" in block.props:
        return str(block.props["title"])
    # 2) first TITLE child text
    t = _first_title_text(block)
    if t:
        return t
    # 3) globals["TITLE"]
    if gvars and "TITLE" in gvars:
        return str(gvars["TITLE"])
    # 4) none
    return None

def _first_title_text(block):
    for ch in block.children:
        if isinstance(ch, Block) and ch.name == "TITLE":
            return "".join(_collect_text(ch))
    return None

def _collect_text(block):
    for ch in block.children:
        if isinstance(ch, str):
            yield ch
        elif isinstance(ch, Block):
            yield from _collect_text(ch)
