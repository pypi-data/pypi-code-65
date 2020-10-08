from django.urls import resolve
from .base import get_menu

def identify_active_links(menu, request):
    found_active = False
    for menuitem in menu:
        if menuitem['type'] == 'menuentry':
            if 'viewname' in menuitem.keys() and resolve(request.path_info).view_name == menuitem['viewname']:
                menuitem['active'] = True
                found_active = True
            elif 'active' in menuitem.keys():
                del menuitem['active']
        if menuitem['type'] == 'menugroup':
            menuitem['entries'], found_active = identify_active_links(menuitem['entries'], request)
            if found_active:
                menuitem['active'] = True
            elif 'active' in menuitem.keys():
                 del menuitem['active']
    return menu, found_active


def menu_middleware(get_response):
    """
    This middleware extracts the menu configuration data
    and adds a menu property to the request instance.

    :param get_response:
    :return: the middleware function
    """

    def middleware(request):
        request.menu, found_active = identify_active_links(get_menu(), request)

        response = get_response(request)

        return response

    return middleware
