"""
A collection of generally useful functions.
"""

import re

def clean_id(id_in):
    """
    Input a string and output is a string that can be used an an ID in HTML
    """
    id_out = id_in.replace(' ', '-')
    id_out = id_out.lower()
    return re.sub(r'[^a-z0-9\_\-]', '', id_out)

def nav_order_from_nav_pagelist(nav_pagelist):
    """
    Uses the nav_pagelist, which is a list of tuples to create a page ordering for
    the navigation. The result is a list of file paths
    """

    nav_order = []
    # Page ordering are the pages (first element for each item in the nav_pagelist)
    # and the BOM pages for these pages (third element in the tuple)
    for page_tuple in nav_pagelist:
        nav_order.append(page_tuple[0])
        if page_tuple[2] is not None:
            nav_order.append(page_tuple[2])
    return nav_order
