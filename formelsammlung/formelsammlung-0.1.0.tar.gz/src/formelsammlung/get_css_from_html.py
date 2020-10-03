# noqa: D205,D208,D400
"""
    get_css_from_html
    ~~~~~~~~~~~~~~~~~
    Extract CSS from HTML.
    :copyright: (c) Christian Riedel
"""
###Func for extracting css files from html source
def get_css_from_html(html_code):
    ###Get start and end index of head section in html source
    start = 6 + html_code.find('<head>') ###6 = len('<head>')
    end = html_code.find('</head>', start)

    ###If either start or end tag is not found return empty list (cancel)
    if start == -1 or end == -1:
        return []

    ###Extract head section from html source; define index values of head section string
    html_head = html_code[start:end]
    end = end - start
    start = 0

    ###Loop trough head section and get all css files
    css_files = list()
    while True:
        ###Get start and end index of link section; if either is not found break the loop
        link_idx_start = html_head.find('<link ', start, end)
        if link_idx_start == -1:
            break
        link_idx_end = html_head.find('>', link_idx_start, end)
        if link_idx_end == -1:
            break
        ###Check if link section is a stylesheet one
        if html_head.find('stylesheet', link_idx_start, link_idx_end):
            ###Get start index of css file; looking for href; continue if found
            css_idx_start = 6 + html_head.find('href=', link_idx_start, link_idx_end) ###6 = len('href=' and the quotes sign after)
            if css_idx_start != 5:
                ###Get end index of css file; looking for same quotes as start; continue if found and css_file string is not empty
                css_idx_end = html_head.find(html_head[css_idx_start - 1], css_idx_start, link_idx_end)
                if css_idx_end != -1 and css_idx_end - css_idx_start > 1:
                    ###Append css file to output list
                    css_file = html_head[css_idx_start:css_idx_end]
                    css_files.append(css_file)
        ###Start new loop after current link section
        start = link_idx_end

    return css_files
