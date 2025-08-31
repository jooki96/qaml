from .template import Template


def resolve_var(name, node, tpl=None, values=None, default=None):
    """
    Resolve a variable value for substitution.

    Resolution order:
      1. If an expose rule maps this variable to an alias,
         check node.attrs[alias].
      2. Directly check node.attrs[name].
      3. Check external values.
      4. Use default.
      5. Fallback: empty string.
    """
    # 1. Check expose rules (alias → original mapping)
    if tpl and tpl.exposed:
        for alias, info in tpl.exposed.items():
            original = info["original"]     # e.g. "class"
            
            if original.upper() != name:    # match $CLASS → "class"
                continue
                
            if alias in node.attrs:     # e.g. .style in QAML
                return node.attrs[alias]

    # 2. Direct attribute lookup
    if name in node.attrs:
        return node.attrs[name]

    # 3. External values
    if values and name in values:
        return values[name]

    # 4. Default from template
    if default is not None:
        return default

    # 5. Fallback
    return ""


def render_node(node, templates, values=None):
    tpl = templates.get(node.name)
    if tpl is None: 
        # no template: just render children
        
        parts = []
        for c in node.children:
            if isinstance(c, str):
                parts.append(c)
            else:
                parts.append(render_node(c, templates, values))
        return "".join(parts)

    out = []
    values = values or {}

    for part in tpl.parts:
        if isinstance(part, str):
            out.append(part)
            continue

        var, default = part
        name = var[1:]  # strip $

        if name == "BODY":
            rendered_children = []
            for c in node.children:
                if isinstance(c, str):
                    rendered_children.append(c)  # raw text
                    continue
                     
                rendered_children.append(render_node(c, templates, values)) 
                
            out.append("".join(rendered_children))
        else:
            val = resolve_var(name, node, tpl=tpl, values=values, default=default)
            out.append(str(val))
    rendered = "".join(out)

    for pat, repl in tpl.defines:
        rendered = rendered.replace(pat, repl)

    return rendered

def render(root, templates, values=None):
    """
    Render a full AST starting at root.
    """
    return render_node(root, templates, values)
