"""
Shared template filters for Django-Flask compatibility

This module provides custom template filters that enable the same template
syntax to work in both Django and Flask applications.

Usage in templates:
    {% load shared_filters %}
    <link rel="stylesheet" href="{{ 'css/style.css'|static }}">
"""
from django import template
from django.templatetags.static import static as django_static

register = template.Library()


@register.filter(name='static')
def static_filter(path):
    """
    Custom template filter to generate static file URLs.
    This allows us to use the same filter syntax for both Flask and Django.
    
    Usage in templates: {{ 'css/style.css'|static }}
    """
    return django_static(path)
