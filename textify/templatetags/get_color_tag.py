import random

from django import template

register = template.Library()

colors = ['#ac2925', '#67b168', 'crimson', 'slategray', 'blueviolet', '#c0a16b']


@register.simple_tag
def get_random_color():
    return random.choice(colors)
