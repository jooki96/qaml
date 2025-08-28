"""QAML: Quick Accessible Markup Language (content-only templating)"""
from .parser import parse_text
from .templates import load_templates
from .renderer import render
from .qaml import load_modules, load_qaml, render_html
__all__ = ["parse_text", "load_templates", "render", "load_modules", "load_qaml", "render_html"]
