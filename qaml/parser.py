import re
from .block import Block

# Inline tag like: [LINK .href="..." .class+="btn"]Click[/LINK]
INLINE_OPEN = re.compile(r"\[(?P<name>[A-Z0-9_:-]+)(?P<attrs>(?:\s+\.[a-zA-Z_][\w:-]*\s*(?:\+=|=)\s*\"[^\"]*\")*)\]")
INLINE_CLOSE = re.compile(r"\[/([A-Z0-9_:-]+)]")
INLINE_ATTR = re.compile(r"\.(?P<key>[a-zA-Z_][\w:-]*)\s*(?P<op>\+=|=)\s*\"(?P<val>[^\"]*)\"")

# Block header like: NAME: [.id="x" .class+="y"]
HEADER = re.compile(r"^(?P<name>[A-Z0-9_:-]+):(?:\s+(?P<attrs>.*))?$")
PROP = re.compile(r"^\.(?P<key>[a-zA-Z_][\w:-]*)\s*(?P<op>\+=|=)\s*\"(?P<val>[^\"]*)\"\s*$")

def _dedent_width(line):
    return len(line) - len(line.lstrip(" \t"))
    
def parse_text(text):
    """Parse QAML source into an AST Block tree.

    Syntax:
      - Indentation defines hierarchy (spaces or tabs; mixed discouraged).
      - Block: NAME: [optional inline props]
      - Property line inside a block: .key="val" or .class+="token"
      - Plain text becomes raw string nodes; supports inline tags [TAG ...]...[/TAG].
      - Lines starting with # are comments.
    """
    lines = text.splitlines()
    # Autodetect indent unit (default 2 spaces)
    unit = None
    for L in lines:
        if L.strip() and (L.startswith(" ") or L.startswith("\t")):
            w = _dedent_width(L)
            if w:
                unit = w
                break
    indent_unit = unit or 2

    # Stack of (indent_level, Block)
    root = Block("__ROOT__")
    stack = [(0, root)]

    i = 0
    n = len(lines)
    while i < n:
        raw = lines[i]
        i += 1
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        indent = _dedent_width(raw)
        if indent % indent_unit != 0:
            raise SyntaxError(f"Indentation not multiple of {indent_unit} at line: {raw!r}")
        level = indent // indent_unit

        # Close blocks until we reach parent level
        while stack and stack[-1][0] > level:
            stack.pop()
        if not stack:
            raise SyntaxError("Invalid indentation structure")
        parent = stack[-1][1]

        # Work with the stripped version only for header/property checks
        line_stripped = raw.strip()

        m = HEADER.match(line_stripped)
        if m:
            blk = Block(m.group("name"))
            # Inline attrs in header
            attrs = m.group("attrs") or ""
            for am in INLINE_ATTR.finditer(attrs):
                blk.add_prop(am.group("key"), am.group("val"), am.group("op"))
            parent.add_child(blk)
            stack.append((level+1, blk))
            continue

        # Property line?
        pm = PROP.match(line_stripped)
        if pm:
            parent.add_prop(pm.group("key"), pm.group("val"), pm.group("op"))
            continue

        # Otherwise it's a text line (may contain inline tags).
        # Slice off the parent's base indent, but preserve inner indentation.
        base_indent = stack[-1][0] * indent_unit
        text_line = raw[base_indent:]  + "\n"

        for node in _parse_inline(text_line):
            parent.add_child(node) 

    return root

def _parse_inline(line):
    """Yield str or Block nodes parsed from inline syntax in a single line."""
    out = []
    pos = 0
    stack = []  # (name, Block)
    while pos < len(line):
        m = INLINE_OPEN.search(line, pos)
        c = INLINE_CLOSE.search(line, pos)
        if m and (not c or m.start() < c.start()):
            # Emit leading text
            if m.start() > pos:
                out.append(line[pos:m.start()])
            blk = Block(m.group("name"))
            attrs = m.group("attrs") or ""
            for am in INLINE_ATTR.finditer(attrs):
                blk.add_prop(am.group("key"), am.group("val"), am.group("op"))
            stack.append((blk.name, blk))
            pos = m.end()
        elif c and stack and c.start() >= pos:
            # close the last block
            if c.group(1) != stack[-1][0]:
                raise SyntaxError(f"Mismatched inline close tag: {c.group(1)} expected {stack[-1][0]}")
            content = line[pos:c.start()]
            for node in _parse_inline(content):
                stack[-1][1].add_child(node)
            blk = stack.pop()[1]
            if stack:
                stack[-1][1].add_child(blk)
            else:
                out.append(blk)
            pos = c.end()
        else:
            # no more tags
            out.append(line[pos:])
            break
    if stack:
        names = ", ".join(n for n,_ in stack)
        raise SyntaxError(f"Unclosed inline tag(s): {names}")
    return out
