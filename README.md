# QAML - Markup and Templating Language

QAML is a human-readable **content-only markup language**.  
It was designed to be **easy to write, easy to parse, and agnostic to output format**.  
You can compile QAML into HTML today, and in the future to **other formats** (Markdown, LaTeX, XML…).

[NOTE: THIS PROJECT IS STILL IN DEVELOPMENT]

---

## 1. QAML as a markup language

QAML is indentation-based, like YAML or Python.  
You define **blocks**, **attributes**, and **text**, with optional inline tags.

### Syntax rules
- **Block**: `NAME:` starts a block.
- **Attributes**: lines starting with `.` set properties.  
  - `.key = "value"` sets/overwrites.  
- **Text lines** become text nodes.  
- **Inline blocks**: `[LINK .href="https://x"]inside[/LINK]`  
- **Comments**: `# …`

### Example
```qaml
TITLE:
    Hello QAML
TEXT:
    This is [LINK .href="https://example.com"]a link[/LINK].
IMG:
    .src = "cover.png"
```

Parsed, this produces a tree of `Node` objects (an AST).

---

## 2. QAML with templates

Templates define how blocks render.  
They live in `.html` or `.t` files with named `[BLOCK]` sections.

---

## 3. Placeholders in templates

### `$BODY`
Replaced by the rendered children of the block.

```html
[TEXT]
<p>$BODY</p>
```

QAML:
```qaml
TEXT:
    Hello world
```

→ `<p>Hello world</p>`

---

### `$EXPOSE attr`
Exposes a QAML attribute as an HTML attribute.

```html
[IMG]
<img $EXPOSE src>
```

QAML:
```qaml
IMG:
    .src = "cover.png"
```

→ `<img src="cover.png">`

---

### `$EXPOSE_AS(prop, attr)`
Expose QAML attribute `.prop` but output as HTML attribute `attr`.

```html
[LINK]
<a $EXPOSE_AS("link", "href")>$BODY</a>
```

QAML:
```qaml
LINK:
    .link = "https://example.com"
    Click me
```

→ `<a href="https://example.com">Click me</a>`

---

### `$DEFINE(x, y)`
Replace text after rendering.

```html
[CODE]
<pre>$DEFINE("  ", "&nbsp;&nbsp;&nbsp;&nbsp;")$BODY</pre>
```

QAML:
```qaml
CODE:
    def add(x, y):
        return x + y
```

→ indented spaces replaced with HTML entities.

---

### `$VAR`
Substituted from QAML attributes or external `values`.

```html
[TITLE]
<h1>$TITLE</h1>
```

QAML:
```qaml
TITLE:
    .title = "Hello QAML"
```

→ `<h1>Hello QAML</h1>`

And with external values:

```python
render_html(ast, templates, values={"TITLE": "Injected Title"})
```

→ `<h1>Injected Title</h1>`

---

## 4. Root template example

```html
[ROOT]
<!DOCTYPE html>
<html>
<head>
  <title>$TITLE</title>
</head>
<body>
$BODY
</body>
</html>
```

---

## 5. Python usage

```python
from qaml.api import load_templates, load_qaml, render_html

templates = load_templates("templates")
ast       = load_qaml("examples/demo.qaml")
html      = render_html(ast, templates, values={"TITLE": "MySite"})

print(html)
```

---

## 6. Why QAML?
- **Readable**: like YAML, but only for structured content. It’s designed for everyday users with minimal training, offering a quick way to format content. QAML aims to reclaim the original simplicity of HTML, which has become bloated, convoluted and strayed from its initial vision.
- **Composable**: you can swap and share templates (basic, bootstrap, tailwind) with ease.
- **Extendable**: can target other formats (LaTeX, Markdown, XML) in the future.
- **Layered**: QAML handles structure and structure only. As a guideline, presentation and logic should live elsewhere (in templates or engines like Jinja).
