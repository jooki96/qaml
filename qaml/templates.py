import os, re, io

SECTION = re.compile(r"^\[(?P<name>[A-Za-z0-9_:-]+)]\s*$")

def load_templates(folder):
    """Load all .html files in *folder* that contain sections like:

        [NAME]
        <div $EXPOSE>$BODY</div>

    Returns dict{name: template_str}.
    Later files override earlier ones.
    """
    templates = {}
    for entry in os.listdir(folder):
        if not entry.endswith(".html"):
            continue
        path = os.path.join(folder, entry)
        with open(path, "r", encoding="utf-8") as f:
            buf = io.StringIO()
            name = None
            for line in f:
                m = SECTION.match(line)
                if m:
                    if name is not None:
                        templates[name] = buf.getvalue().rstrip()
                        buf = io.StringIO()
                    name = m.group("name")
                else:
                    buf.write(line)
            if name is not None:
                templates[name] = buf.getvalue().rstrip()
    return templates
