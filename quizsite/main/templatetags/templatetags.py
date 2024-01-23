from django import template

register = template.Library()


@register.inclusion_tag('main/show_menu.html')
def show_menu(request):
    return {'request': request}
