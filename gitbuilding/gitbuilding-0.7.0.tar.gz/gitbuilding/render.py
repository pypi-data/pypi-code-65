"""
This contains GBRenderer, the class responsible for rendering processed markdown into HTML
It also contains the URLRules GitBuilding uses for HTML and some other helper functions.
"""

import os
import posixpath
import codecs
import datetime
import re
from copy import copy, deepcopy
import logging
from markdown import markdown
from jinja2 import Environment, FileSystemLoader
from gitbuilding.buildup import URLRules
from gitbuilding import utilities
from gitbuilding.buildup.buildup import IMAGE_REGEX, LINK_REGEX

_LOGGER = logging.getLogger('BuildUp.GitBuilding')

class URLRulesHTML(URLRules):
    """
    The BuildUp URLRules used in GitBuilding for both the server and the static HTML.
    This is a child-class of buildup.URLRules with functions to strip off '.md' file
    extensions, rerouted stl links (for parts only) to markdown pages, and to replace
    empty links with "missing".
    """
    def __init__(self, rel_to_root=False):

        super(URLRulesHTML, self).__init__(rel_to_root=rel_to_root)
        def fix_missing(url, anchor):
            if url == "" and  anchor == "":
                return "missing", anchor
            return url, anchor

        def stl_to_page(url, anchor):
            if url.endswith('.stl'):
                return url[:-4], anchor
            return url, anchor

        def md_to_page(url, anchor):
            if url.endswith('.md'):
                return url[:-3], anchor
            return url, anchor

        self.add_modifier(fix_missing)
        self.add_modifier(md_to_page)
        self.add_part_modifier(stl_to_page)

class URLRulesPDF(URLRules):
    """
    The BuildUp URLRules used in GitBuilding PDF generation (via single pageHTML).
    This is a child-class of buildup.URLRules with functions to strip off '.md' file
    """
    def __init__(self, rel_to_root=True):

        super(URLRulesPDF, self).__init__(rel_to_root=rel_to_root)

        def md_to_inside_page(url, anchor):
            if url.endswith('.md'):
                url = url[:-3]
                url = url.replace('/', '__')
                if anchor != '':
                    anchor = url + '---' + anchor
                else:
                    anchor = url
                url = ''
            return url, anchor

        def jpg_to_png(url, anchor):
            if url.lower().endswith((".jpg", ".jpeg")):
                url = '.'.join(url.split('.')[:-1])+'.png'
            return url, anchor

        self.add_modifier(md_to_inside_page)
        self.add_modifier(jpg_to_png)


def _is_active_nav_item(nav_item, link):
    """
    Checks if the item in the navigation dictionary or any of the
     terms in the sub-navigation are the active page
    """
    if nav_item["link"] == link:
        return True
    if "subnavigation" in nav_item:
        for sub_nav_item in nav_item["subnavigation"]:
            if _is_active_nav_item(sub_nav_item, link):
                return True
    return False

def format_warnings(warnings):
    """
    Returns warnings for the live renderer to display
    """
    output = ""
    for warning in warnings:
        if warning["fussy"]:
            cssclass = "fussywarning"
            warntype = "FussyWarning"
        else:
            cssclass = "warning"
            warntype = "Warning"
        output += f'<p class="{cssclass}">{warntype}: {warning["message"]}</p>\n'
    return output

def _replace_stls(md):
    """
    Find links to an STL on their own line. Replace with live viewer.
    """

    links = re.findall(r"^"+LINK_REGEX, md, re.MULTILINE)
    stls = [link for link in links if link[2].endswith('.stl')]
    for stl in stls:
        viewer_code = (f'[{stl[1]}]({stl[2]})\n'
                       f'<stl-part-viewer src="{stl[2]}" width="500" height="500"'
                       ' floorcolor="0xf1f1f1"></stl-part-viewer>')
        md = md.replace(stl[0], viewer_code)
    return md

class GBRenderer:
    """
    This class is the renderer for GitBuilding HTML
    """
    FULLPAGE = 0
    IFRAME = 1
    PDFPAGE = 2

    def __init__(self, config, root="/", static=True):

        self.config = config
        self.author_list = utilities.author_list(self.config)
        self._static = static
        self.root = root
        self.custom_stylesheets = []
        self.custom_favicons = {'ico': [], 'png': []}
        # Variables that can be accessed by custom Footer/Header
        self.populate_vars()
        self.scan_assets()
        self._url_rules = URLRulesHTML()

        custom_path = os.path.join('.', '_templates')
        this_dir = os.path.dirname(__file__)
        template_path = os.path.join(this_dir, 'templates')
        static_path = os.path.join(this_dir, 'static')
        loader = FileSystemLoader([custom_path, template_path, static_path])
        self.env = Environment(loader=loader, trim_blocks=True)

    def populate_vars(self):
        """
        This function populates the list of variables that can be used in
        custom headers and footers
        """
        self._variables = {"title": self.config.title,
                           "year": datetime.datetime.now().year,
                           "root": self.root}

        self._variables["authors"] = self.author_list
        self._variables["email"] = self.config.email
        self._variables["affiliation"] = self.config.affiliation
        if self.config.license is None:
            self._variables["license"] = None
        else:
            if self.config.license_file is None:
                self._variables["license"] = self.config.license
            else:
                licence_url = self.config.license_file
                if licence_url.endswith('.md'):
                    licence_url = licence_url[:-3]
                self._variables["license"] = (f'<a href="{self.root}{licence_url}">'
                                              f'{self.config.license}</a>')

        for key in self.config.variables.keys():
            self._variables[key] = self.config.variables[key]


    def _get_variables(self, link=None):
        """
        link is used to change the url roots to relatative. Set link=None to use WebsiteRoot from
        the configuration file.
        """
        variables = copy(self._variables)
        if link is not None:
            relative_root = posixpath.relpath('.', posixpath.dirname(link)) + '/'
            variables['root'] = relative_root
        return variables

    def scan_assets(self):
        """
        This scans the assets folder of the project to look for custom CSS and favicons
        """
        if os.path.exists("assets"):
            for root, _, files in os.walk("assets"):
                for filename in files:
                    filepath = os.path.join(root, filename)
                    if filepath.endswith(".css"):
                        self.custom_stylesheets.append(filepath)
                    if filename == "favicon.ico":
                        self.custom_favicons['ico'].append(filepath)

                    match = re.match(r"^favicon-([0-9]+)x[0-9]+\.png$", filename)
                    if match is not None:
                        self.custom_favicons['png'].append((filepath, match.group(1)))

    def nav_links(self, link=None):
        """
        This function returns the side navigation
        """

        navigation = deepcopy(self.config.navigation)
        for nav_item in navigation:
            if _is_active_nav_item(nav_item, link):
                nav_item['class'] = 'active'
            else:
                nav_item['class'] = 'not-active'
            if "subnavigation" in nav_item:
                for sub_nav_item in nav_item["subnavigation"]:
                    if _is_active_nav_item(sub_nav_item, link):
                        sub_nav_item['class'] = 'active'
                    else:
                        sub_nav_item['class'] = 'not-active'

        tmpl = self.env.get_template("nav.html.jinja")
        html = tmpl.render(navigation=navigation, **self._get_variables(link))
        return html

    def project_header(self, subtitle=None, link=None):
        """
        This is the project header that can be customised.
        """
        tmpl = self.env.get_template("header.html.jinja")
        html = tmpl.render(subtitle=subtitle, **self._get_variables(link))
        return html

    def project_footer(self, link=None):
        """
        This returns either the standard project footer or the customised footer
        """
        tmpl = self.env.get_template("footer.html.jinja")
        html = tmpl.render(**self._get_variables(link))
        return html

    def favicon_html(self):
        """
        This returns the HTML for the favicon. Generates multiple PNG as well
        as ico favicon references based on the custom favicons found.
        """
        tmpl = self.env.get_template("favicon.html.jinja")
        num_custom_favicons = (len(self.custom_favicons['ico'])
                               + len(self.custom_favicons['png']))
        if num_custom_favicons == 0:
            ico_favicons = ["static/Logo/favicon.ico"]
            png_favicons = [("static/Logo/favicon-32x32.png", 32),
                            ("static/Logo/favicon-16x16.png", 16)]
        else:
            ico_favicons = self.custom_favicons['ico']
            png_favicons = self.custom_favicons['png']
        output = tmpl.render(root=self.root,
                             ico_favicons=ico_favicons,
                             png_favicons=png_favicons)
        return output

    def _replace_galleries(self, md):
        """
        Find galleries in the markdown a line with only images (must be more than
        one image) replace with gallery HTML
        """

        tmpl = self.env.get_template("gallery.html.jinja")
        imlines = re.findall(r'^((?:[ \t]*'+IMAGE_REGEX+'[ \t]*(?:\n|\r\n)?){2,})$',
                             md,
                             re.MULTILINE)
        # imlines uses the IMAGE_REGEX which matches lots of groups. First is the whole line.
        imlines = [line[0] for line in imlines]

        for gallery_number, imline in enumerate(imlines):
            images = re.findall(IMAGE_REGEX, imline)
            gallery_html = tmpl.render(gallery_number=gallery_number,
                                       images=images)
            md = md.replace(imline, gallery_html)
        return md

    def render_md(self, md, link=None, **kwargs):
        """
        This function returns the rendered HTML for input markdown
        """
        template = kwargs.get('template', self.FULLPAGE)
        if template != self.PDFPAGE:
            md = self._replace_galleries(md)
            md = _replace_stls(md)

        content_html = markdown(md, extensions=["markdown.extensions.tables",
                                                "markdown.extensions.attr_list",
                                                "markdown.extensions.fenced_code"])
        return self.render(content_html, link=link, **kwargs)

    def render(self, html, link=None, **kwargs):
        """
        This function creates the full HTML page from the input HTML generated from BuildUp
        """
        template = kwargs.get('template', self.FULLPAGE)
        nav = kwargs.get('nav', True)
        editorbutton = kwargs.get('editorbutton', False)

        if link is None:
            editor_link = "-/editor"
        else:
            editor_link = f"/{link}/-/editor"

        input_dictionary = {'favicon_html': self.favicon_html(),
                            'content': html,
                            'nav': nav,
                            'nav_links': self.nav_links(link),
                            'project_header': self.project_header(link=link),
                            'project_footer': self.project_footer(link),
                            'static': self._static,
                            'editorbutton': editorbutton,
                            'editor_link': editor_link}

        if template == self.FULLPAGE:
            tmpl = self.env.get_template("full_page.html.jinja")
            input_dictionary['custom_stylesheets'] = self.custom_stylesheets
        elif template == self.IFRAME:
            tmpl = self.env.get_template("iframe.html.jinja")
            custom_style = []
            for sheet in self.custom_stylesheets:
                with codecs.open(sheet, mode="r", encoding="utf-8") as css_file:
                    custom_style.append(css_file.read())
            input_dictionary['custom_style'] = custom_style
        elif template == self.PDFPAGE:
            page_id = link.replace('/', '__')
            tmpl = self.env.get_template("pdfpage.html.jinja")
            input_dictionary['page_id'] = page_id
        else:
            raise ValueError(f'Unknown pdf template type: {template}')
        output = tmpl.render(**input_dictionary, **self._get_variables(link))

        return output

    def missing_page(self):
        """
        This returns an HTML page for missing parts.
        """
        return self.render("<h1>GitBuilding Missing Part</h1>")

    def empty_homepage(self):
        """
        This returns an HTML page for the homepage if missing. This is only
        shown on the live server.
        """
        html = (r'<h1>No homepage set</h1>'
                r'<h2><a href="/-/create-homepage/">Create homepage</a></h2>')
        return self.render(html, editorbutton=False)

    def contents_page(self, file_list):
        """
        Returns an HTML page that lists all the documentation pages in the project.
        """
        url_translator = self._url_rules.create_translator('-/contents-page')
        md_pages = []
        for file_obj in file_list:
            if file_obj.path.endswith('.md'):
                web_path = url_translator.simple_translate(file_obj.path)
                md_pages.append([file_obj.path, web_path])
        md_pages.sort(key=lambda x: (len(x[1].split('/')), x[0].lower()))
        tmpl = self.env.get_template("contents.html.jinja")
        html = tmpl.render(md_pages=md_pages)
        return self.render(html, editorbutton=False)

    def stl_page(self, stl_file):
        """
        This returns an HTML page with a live 3D view of the input STL file.
        """
        model_name = os.path.basename(os.path.splitext(stl_file)[0])
        stl_md = f"# {model_name}\n\n"
        stl_md += f"[Download STL]({self.root}{stl_file})\n\n"
        return self.render_md(stl_md,
                              os.path.splitext(stl_file)[0],
                              editorbutton=False)

    def full_pdf(self, html_content, subtitle):
        """
        This method takes all pages as a combined block of html. It then uses the
        full_pdf template to generate an HTML file that WeasyPrint can use to create
        a PDF file.
        """
        pdf_title = self._variables['title']
        if pdf_title is not None and subtitle is not None:
            pdf_title += f' -- {subtitle}'
        tmpl = self.env.get_template("full_pdf.html.jinja")
        html = tmpl.render(content=html_content,
                           project_header=self.project_header(subtitle=subtitle),
                           project_footer=self.project_footer(),
                           pdf_title=pdf_title,
                           **self._get_variables())
        return html
