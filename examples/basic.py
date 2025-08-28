# 01_basic_compile.py
from qaml import load_modules, load_qaml, render_html

modules = load_modules("modules/basic")                     # load templates from modules/templates.html
qaml_ast     = load_qaml("demo.qaml")              # parse QAML into AST
html    = render_html(qaml_ast, modules)                    # render to HTML

open("out.html", "w", encoding="utf-8").write(html)