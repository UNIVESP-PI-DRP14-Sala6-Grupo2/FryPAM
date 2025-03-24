from django import template

register = template.Library()

@register.filter
def custom_getattr(obj, attr):
    return getattr(obj, attr)

@register.filter
def get_dict_item(dictionary, key):
    return dictionary.get(key, '')