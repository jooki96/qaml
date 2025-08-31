import re

# ------------------------------------
# Regex patterns
# ------------------------------------
attr_line_re = re.compile(r'^\.(\w+)\s*=\s*(.+)$')         # .key = value
inline_block_re = re.compile(r'\[([A-Z0-9_]+)(.*?)\](.*?)\[/\1\]')  # string contains inline block

# inline_open_re = re.compile(r'^\[(\w+)(.*?)\]$')           # [BLOCK ...]
# inline_close_re = re.compile(r'^\[/(\w+)\]$')              # [/BLOCK]
attr_inline_re = re.compile(r'\.(\w+)="([^"]*)"')          # .key="value"
block_re = re.compile(r'^([A-Z0-9_]+):$')

# ------------------------------------
# AST Node
# ------------------------------------
class Node:
    def __init__(self, name, attrs=None, children=None):
        self.name = name
        self.attrs = attrs or {}
        self.children = children or []

    def __repr__(self, level=0):
        pad = "  " * level
        rep = f"{pad}{self.name} {self.attrs}\n"
        for c in self.children:
            if isinstance(c, Node):
                rep += c.__repr__(level + 1)
            else:  # raw string child
                rep += f"{pad}  {repr(c)}\n"
        return rep

# ------------------------------------
# Attribute parsing helpers
# ------------------------------------
def parse_attr_line(line):
    """Parse `.key = value` style attributes (indent blocks)."""
    m = attr_line_re.match(line)
    if not m:
        return None
    key, val = m.groups()
    val = val.strip()
    # naive type coercion
    if val.startswith('"') and val.endswith('"'):
        val = val[1:-1]
    elif val.isdigit():
        val = int(val)
    elif val.lower() in ("true", "false"):
        val = (val.lower() == "true")
    return key, val


def parse_inline_attrs(text):
    """Parse .key="val" attributes inside inline blocks."""
    attrs = {}
    for k, v in attr_inline_re.findall(text):
        if v.isdigit():
            v = int(v)
        elif v.lower() in ("true", "false"):
            v = (v.lower() == "true")
        attrs[k] = v
    return attrs


def parse_inline_in_text(text):
    """Split a text string into raw segments and inline block Nodes."""
    children = []
    pos = 0
    for m in inline_block_re.finditer(text):
        start, end = m.span()

        # text before block
        if start > pos:
            children.append(text[pos:start])

        block_name = m.group(1)
        attr_text  = m.group(2).strip()
        body_text  = m.group(3).strip()

        # parse inline attrs
        attrs = parse_inline_attrs(attr_text)

        # recursively parse inner body (nested inline blocks allowed)
        body_children = parse_inline_in_text(body_text) if body_text else []

        children.append(Node(block_name, attrs=attrs, children=body_children))

        pos = end

    # trailing text after last match
    if pos < len(text):
        children.append(text[pos:])

    return children

    
# ------------------------------------
#   QAML parser
# ------------------------------------
def parse_qaml(text): 
    root = Node("ROOT")
    stack = [(0, root)]

    for line in text.splitlines():
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip() 

        # Block header
        if block_re.match(stripped):
            node = Node(stripped[:-1])  # drop trailing ':'

            # pop back until we find the right parent, but never remove root
            while len(stack) > 1 and indent <= stack[-1][0]:
                stack.pop()
 
            stack[-1][1].children.append(node)
            stack.append((indent, node))
            continue

        # Attribute line
        attr = parse_attr_line(stripped)
        if attr:
            k, v = attr
            stack[-1][1].attrs[k] = v
            continue
            
        # do we need these anymore?
        # inline_open = inline_open_re.match(stripped)
        # if inline_open:
            # name, attr_text = inline_open.groups()
            # node = Node(name)
            # node.attrs.update(parse_inline_attrs(attr_text)) 
            # stack_top_node = stack[-1][1]
            # stack_top_node.children.append(node)
            # stack.append((indent, node))
            # continue
            
        # inline_close = inline_close_re.match(stripped)
        # if inline_close:
            # close_name = inline_close.group(1) 
            # while len(stack) > 1 and stack[-1][1].name != close_name:
                # bad_node = stack.pop()[1] 
                # stack[-1][1].children.remove(bad_node)
            # if len(stack) > 1 and stack[-1][1].name == close_name:
                # stack.pop()
            # continue
            
            
        stack[-1][1].children.extend(parse_inline_in_text(stripped))
        
        
    return root 