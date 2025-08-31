import re

# reuse parse_template from before
# (keeps Template class and directive handlers)

# -----------------------------
# Regex
# -----------------------------

tmpl_re = re.compile(r'\$([A-Z_][A-Z0-9_]*)(\((.*?)\))?')
attr_re = re.compile(r'([a-zA-Z_:][\w:-]*)="([^"]*)"')
tmpl_group_re = re.compile(r'(?m)^\[([A-Z0-9_]+)\]\s*\n([\s\S]*?)(?=^\[[A-Z0-9_]+\]|\Z)')

# -----------------------------
# Template class
# -----------------------------
class Template:
    def __init__(self, raw, parts, exposed, vars_dict, defines):
        self.raw = raw
        self.parts = parts        # list of text segments
        self.exposed = exposed    # dict of exposed attrs
        self.vars = vars_dict     # dict of variable mappings
        self.defines = defines    # list of (pattern, replacement)

    def __repr__(self):
        return (
            f"<Template "
            f"exposed={self.exposed} "
            f"vars={self.vars} "
            f"defines={self.defines}>"
        )  



# -----------------------------
# Core helpers
# -----------------------------
def consume_attribute(text, start):
    """Find the next key="val" attribute after position `start`."""
    m = attr_re.search(text, start)
    if not m:
        return None, None, start
    key, val = m.groups()
    return key, val, m.end()
    
    
# -----------------------------
# Directive handlers
# -----------------------------
def handle_expose(text, pos, exposed):
    key, val, new_pos = consume_attribute(text, pos)
    if key:
        exposed[key] = {
            "original": key,
            "alias": key,
            "default": val 
        }
        return new_pos
    return pos

def handle_expose_as(text, pos, alias, exposed):
    key, val, new_pos = consume_attribute(text, pos)
    if key:
        exposed[alias] = {
            "original": key,   # real HTML attr (e.g. "href")
            "alias": alias,    # QAML-facing name (e.g. "link")
            "default": val     # default value from template ("" if empty)
        }
        return new_pos
    return pos


# def handle_var(text, pos, vars_dict):
    # key, val, new_pos = consume_attribute(text, pos)
    # if key and val.startswith("$"):
        # vars_dict[key] = val[1:]  # strip leading $
        # return new_pos
    # return pos


def handle_define(args, defines):
    if args and len(args) >= 2:
        pattern, replacement = args[0], args[1]
        defines.append((pattern, replacement)) 
    
    
# -----------------------------
# Parser
# -----------------------------

def parse_templates(text):
    """
    Split a templates.t file into multiple Template objects.
    Returns dict: {name: Template}
    """
    templates = {}
    for name, body in tmpl_group_re.findall(text):
        templates[name] = parse_template(body.strip())
    return templates 
    
    
    
    
def parse_template(text):
    parts = []
    exposed = {}
    vars_dict = {}
    defines = []

    i = 0
    while i < len(text):
        m = tmpl_re.search(text, i)
        if not m:
            parts.append(text[i:])
            break

        # raw text before directive
        if m.start() > i:
            parts.append(text[i:m.start()])

        cmd = m.group(1)
        args = m.group(3)
        args = [a.strip().strip('"') for a in args.split(",")] if args else None

        if cmd == "EXPOSE":
            i = handle_expose(text, m.end(), exposed)
            continue
        elif cmd == "EXPOSE_AS":
            alias = args[0] if args else None
            i = handle_expose_as(text, m.end(), alias, exposed)
            continue 
        elif cmd == "DEFINE":
            handle_define(args, defines)
            i = m.end()
            continue
            
        else:                   #FALLBACK handle as a var
            varname = cmd
            default = None
            # if arguments exist, treat them as default value
            if args and len(args) > 0:
                default = args[0]
            vars_dict[varname] = default
            parts.append((f"${varname}", default))
            i = m.end()
            continue
            
            
        # unknown directive: keep as token
        # parts.append((cmd, args))
        i = m.end()

    return Template(text, parts, exposed, vars_dict, defines)