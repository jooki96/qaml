
# QAML - Markup and Templating Language

QAML is a human-readable **content-only markup language**.  
It was designed to be **easy to write, easy to parse, and agnostic to output format**.  
You can compile QAML into HTML, or in the future to **any other format** (Markdown, LaTeX, XML…).

[NOTE: THIS PROJECT IS STILL IN THE DEVELOPMENT PHASE]

---

## 1. QAML as a markup language

QAML is indentation-based, like YAML or Python.  
You define **blocks**, **properties**, and **text**, with optional inline tags.

### Syntax rules
- **Block**: `NAME:` starts a block.
- **Properties**: lines starting with `.` set attributes.  
  - `.key = "value"` overwrite  
  - `.class += "token"` append
- **Text lines** become text nodes.
- **Inline tags**: `[LINK .href="https://x"]inside[/LINK]`
- **Comments**: `# …`

### Example (pure QAML)
```
TITLE:
    Hello QAML
TEXT:
    This is [LINK .href="https://example.com"]a link[/LINK].
IMG:
    .src = "cover.png"
```

Parsed, this is just an AST (Abstract Syntax Tree).

---

## 2. QAML as a templating system

To make QAML useful, we connect it to **templates**.  
A template is just a `.html` file with named sections:

```html
[TITLE]
<h1 $EXPOSE class>$BODY</h1>

[TEXT]
<p $EXPOSE class>$BODY</p>

[LINK]
<a $EXPOSE href>$BODY</a>

[IMG]
<img $EXPOSE src $EXPOSE alt/>
```

Each QAML block (`TITLE`, `TEXT`, `LINK`, `IMG`) is mapped to its template.  
Placeholders (`$BODY`, `$EXPOSE attr`, `$EXPOSE_AS prop -> attr`, `$$GLOBAL`, `$DEFINE`) are replaced during rendering.

---

## 3. Rendering to HTML

### Example
QAML:
```
ROOT:
    .title = "Demo Page"
    TITLE:
        Hello QAML
    TEXT:
        This is [LINK .href="https://example.com"]a link[/LINK].
```

Template `[ROOT]`:
```html
<!DOCTYPE html>
<html>
<head><title>$TITLE</title></head>
<body>
$BODY
</body>
</html>
```

Result:
```html
<!DOCTYPE html>
<html>
<head><title>Demo Page</title></head>
<body>
<h1>Hello QAML</h1>
<p>This is <a href="https://example.com">a link</a>.</p>
</body>
</html>
```

---

## 4. Integration with Jinja

QAML templates may contain **Jinja code**.  
The pipeline is:

1. **QAML → HTML** (placeholders like `$EXPOSE`, `$BODY`, `$$VARS` are resolved).
2. **Jinja render** (loops, conditionals, context injection).

### Example `[ARTICLE]` template
```html
[ARTICLE]
<article>
  {% for item in items %}
    <h2>{{ item.title }}</h2>
    <p>{{ item.text }}</p>
  {% endfor %}
</article>
```

QAML:
```
ARTICLE:
```

Rendered QAML inserts this `<article>...</article>` block,  
then Jinja takes over to expand the `{% for … %}` loop.

---

## 5. Placeholders in templates

- `$BODY` – rendered children.
- `$EXPOSE attr` – emit `attr="value"` if that prop exists.
- `$EXPOSE_AS(prop, attr)` – use `.prop` but output as `attr`.
- `$EXPOSE_ALL` – exposes all properties.
- `$TITLE` – derived from `ROOT`’s `.title`, or first `TITLE:`. 
- `$DEFINE(x, y)` – string replacement. replaces all X with Y. 

---

## 6. Python usage

```python
from qaml.api import load_modules, load_qaml, render_html

mods = load_modules("modules/basic")
ast  = load_qaml("examples/demo.qaml")
html = render_html(ast, mods, globals={"SITE":"MySite"})

print(html)
```

---

## 7. Why QAML?

- **Readable**: like YAML, but only for structured content. It’s designed for everyday users with minimal training, offering a quick way to format content. QAML aims to reclaim the original simplicity of HTML, which has become bloated, convoluted and strayed from its initial vision.
- **Composable**: you can swap and share templates (basic, bootstrap, tailwind) with ease.
- **Extendable**: can target **other formats** (LaTeX, Markdown, XML) in the future.
- **Layered**: QAML handles structure and structure only. As a guideline, presentation and logic should live elsewhere (in templates or engines like Jinja).

---
