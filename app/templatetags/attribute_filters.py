from django import template

register = template.Library()

@register.filter(name='hasattr')
def hasattr_filter(obj, attr_name):
    return hasattr(obj, attr_name)