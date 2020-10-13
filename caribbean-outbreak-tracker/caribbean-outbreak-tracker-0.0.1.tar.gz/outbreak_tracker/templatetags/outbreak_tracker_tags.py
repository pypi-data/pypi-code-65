from django import template

register = template.Library()

@register.simple_tag(name='grand_total_cases')
def total_cases(virus_code):
    return virus_code

@register.simple_tag(name='grand_total_new_cases')
def total_new_cases(virus_code):
    return virus_code

@register.simple_tag(name='grand_total_deaths')
def total_deaths(virus_code):
    return virus_code

@register.simple_tag(name='grand_total_new_deaths')
def total_new_deaths(virus_code):
    return virus_code

@register.simple_tag(name='grand_total_recovered')
def recovered(virus_code):
    return virus_code