from django import template

register = template.Library()

@register.filter
def mul(a, b):
    return a * b 
