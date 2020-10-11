from django.shortcuts import render


def make_view(page_name):
    """
    Create a view that render the page specified in page_name. [DRY]
    """
    return lambda request: render(request, 'adminlte/demo/' + page_name)
