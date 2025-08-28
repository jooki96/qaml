class Block:
    """Minimal AST node for a QAML block.

    name: str        (e.g., ROOT, TEXT, IMG)
    props: dict      (attributes)
    children: list   (items are either Block instances or plain strings for text)
    """
    __slots__ = ("name", "props", "children")
    def __init__(self, name):
        self.name = name
        self.props = {}
        self.children = []
    def add_prop(self, key, value, op="="):
        if op == "+=" and key in ("class", "className"):
            prev = self.props.get("class", "")
            self.props["class"] = (prev + " " + value).strip()
        else:
            self.props[key] = value
    def add_child(self, node):
        # node can be a Block or a plain string
        self.children.append(node)
    def __repr__(self):
        return f"Block({self.name!r}, props={self.props!r}, children={len(self.children)})"
