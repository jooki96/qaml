"""QAML: Quick Accessible Markup Language (content-only templating)"""
# from .parser import parse_qaml
# from .template import parse_template, parse_templates
# from .renderer import render
from .qaml import load_templates, load_qaml, render_html
__all__ = ["load_modules", "load_qaml", "render_html"]
