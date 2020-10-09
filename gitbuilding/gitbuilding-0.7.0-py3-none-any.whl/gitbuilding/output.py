"""
This module handles all the Builder classes that produce outputs.
Currently the outputs are
* HTML provided by StaticSiteBuilder
* Markdown provided by MarkdownBuilder
to make a custom Builder you can inherit from the Builder class.
"""

import os
import sys
import shutil
import logging
import re
from tempfile import gettempdir
try:
    from PIL import Image
    from weasyprint import HTML
except ImportError:
    pass
from gitbuilding.render import GBRenderer, URLRulesHTML, URLRulesPDF
from gitbuilding.buildup import Documentation, URLRules, read_directory
from gitbuilding.config import load_config_from_file
from gitbuilding import utilities
import gitbuilding.buildup.utilities as buildup_utilities

_LOGGER = logging.getLogger('BuildUp.GitBuilding')

class Builder():
    """
    Base class for Builder classes. Do not use this class.
    """

    def __init__(self, conf, url_rules, rem_title=False, rem_bottom_nav=False):
        """
        `conf is the configuration file`
        rem_title is set to true to override configuration and
        remove the title from the landing page
        """
        configuration = load_config_from_file(conf)
        if rem_title:
            configuration.remove_landing_title = True
        if rem_bottom_nav:
            configuration.remove_bottom_nav = True
        license_file = utilities.handle_licenses(configuration)
        self._doc = Documentation(configuration, url_rules)
        file_list = read_directory('.', exclude_list=configuration.exclude)
        if license_file is not None:
            file_list.append(license_file)
        self._doc.buildall(file_list)
        self._out_dir = "_build"

    @property
    def doc(self):
        """
        Returns the buildup Documentation object for the site.
        """
        return self._doc

    def _make_clean_directory(self):
        """
        Make a clean and empty directory for the static html
        """
        if os.path.exists(self._out_dir):
            shutil.rmtree(self._out_dir)
        os.mkdir(self._out_dir)

    def build(self):  # pylint: disable=no-self-use
        """
        This method should be overridden for in derived classes
        """
        raise RuntimeError('`build` should be overridden by other Builder classes')

    def _build_file(self, outfile):
        """
        Writes the output for any buildup page and copies over other
        output files
        """

        if outfile.path.startswith('..'):
            _LOGGER.warning('Skipping %s.', outfile.path)
            return
        full_out_path = os.path.join(self._out_dir, outfile.path)
        full_out_dir = os.path.dirname(full_out_path)
        if not os.path.exists(full_out_dir):
            os.makedirs(full_out_dir)
        if outfile.dynamic_content:
            self._build_dynamic_conent(outfile, full_out_path)
        else:
            self._build_static_conent(outfile, full_out_path)

    def _build_dynamic_conent(self, outfile, full_out_path):
        pass

    def _build_static_conent(self, outfile, full_out_path): #pylint: disable=no-self-use
        if os.path.exists(outfile.location_on_disk):
            if not os.path.isdir(outfile.location_on_disk):
                shutil.copy(outfile.location_on_disk, full_out_path)

class MarkdownBuilder(Builder):
    """
    Class to build a markdown directory from a BuildUp directory.
    """

    def __init__(self, conf, url_rules=None):
        """
        `conf is the configuration file`
        """

        if url_rules is None:
            url_rules = URLRules(rel_to_root=False)

        def fix_missing(url, anchor):
            if url == "" and  anchor == "":
                return "missing.md", anchor
            return url, anchor

        url_rules.add_modifier(fix_missing)

        super(MarkdownBuilder, self).__init__(conf, url_rules)


    def _write_missing_page(self):
        """
        Write the page for any part which is missing from the documentation
        """
        missing_page_file = os.path.join(self._out_dir, "missing.md")
        with open(missing_page_file, "w", encoding='utf-8') as html_file:
            html_file.write("# GitBuilding Missing Part")

    def _build_dynamic_conent(self, outfile, full_out_path):
        with open(full_out_path, "w", encoding='utf-8') as output_file:
            output_file.write(outfile.content)

    def build(self):
        """
        Builds the whole markdown folder
        """

        self._make_clean_directory()
        self._write_missing_page()
        for outfile in self.doc.output_files:
            self._build_file(outfile)

class StaticSiteBuilder(Builder):
    """
    Class to build a static website from a BuildUp directory.
    """

    def __init__(self, conf, url_rules=None, root=None, rem_bottom_nav=False):
        """
        `conf is the configuration file`
        """
        self._stl_page = True
        if url_rules is None:
            url_rules = URLRulesHTML()

        super(StaticSiteBuilder, self).__init__(conf,
                                                url_rules,
                                                rem_title=True,
                                                rem_bottom_nav=rem_bottom_nav)
        if root is None:
            root = self._doc.config.website_root
        self._renderer = GBRenderer(self._doc.config, root=root)

        # site dir is not setable as we would then need to do all the checks for
        # not writing over a specific directory
        self._out_dir = "_site"

    def _write_missing_page(self):
        """
        Write the page for any part which is missing from the documentation
        """
        missing_page_file = os.path.join(self._out_dir, "missing.html")
        with open(missing_page_file, "w", encoding='utf-8') as html_file:
            html_file.write(self._renderer.missing_page())

    def _build_dynamic_conent(self, outfile, full_out_path):
        if outfile.path.endswith('.md'):
            self._markdown_content(outfile, full_out_path)
        else:
            with open(full_out_path, "w", encoding='utf-8') as file_obj:
                file_obj.write(outfile.content)

    def _markdown_content(self, outfile, full_out_path):
        if outfile.path == self.doc.config.landing_page:
            full_out_path = os.path.join(self._out_dir, "index.html")
        else:
            full_out_path = os.path.splitext(full_out_path)[0]+'.html'
        with open(full_out_path, "w", encoding='utf-8') as html_file:
            page_html = self._renderer.render_md(outfile.content,
                                                 os.path.splitext(outfile.path)[0],
                                                 editorbutton=False)
            html_file.write(page_html)

    def _build_static_conent(self, outfile, full_out_path):
        if self._stl_page:
            if os.path.splitext(full_out_path)[1] == '.stl':
                html_path = os.path.splitext(full_out_path)[0]+'.html'
                with open(html_path, "w", encoding='utf-8') as html_file:
                    page_html = self._renderer.stl_page(outfile.path)
                    html_file.write(page_html)
        super(StaticSiteBuilder, self)._build_static_conent(outfile, full_out_path)

    def _copy_static_files(self):
        """
        Copies all the static web files that come as default with gitbuilding.
        This includes the CSS, the favicons, and the 3D viewer
        """
        gbpath = os.path.dirname(__file__)
        static_dir = os.path.join(gbpath, "static")
        for root, _, files in os.walk(static_dir):
            for filename in files:
                if not "live-editor" in root or "local-server" in root:
                    filepath = os.path.join(root, filename)
                    out_file = os.path.join(self._out_dir, os.path.relpath(filepath, gbpath))
                    out_dir = os.path.dirname(out_file)
                    if not os.path.exists(out_dir):
                        os.makedirs(out_dir)
                    shutil.copy(filepath, out_file)

    def _copy_local_assets(self):
        """
        Copies all assets from the local directory. This is custom CSS and favicons
        """
        for root, _, files in os.walk("assets"):
            for filename in files:
                filepath = os.path.join(root, filename)
                out_file = os.path.join(self._out_dir, filepath)
                out_dir = os.path.dirname(out_file)
                if not os.path.exists(out_dir):
                    os.makedirs(out_dir)
                shutil.copy(filepath, out_file)

    def build(self):
        """
        Builds the whole static site
        """

        self._make_clean_directory()
        self._write_missing_page()
        for outfile in self.doc.output_files:
            self._build_file(outfile)
        self._copy_static_files()
        if os.path.exists("assets"):
            self._copy_local_assets()

class PdfBuilder(StaticSiteBuilder):
    """
    Class to build a static website from a BuildUp directory.
    """

    def __init__(self, conf, url_rules=None):
        """
        `conf is the configuration file`
        """
        if url_rules is None:
            url_rules = URLRulesPDF()
        super(PdfBuilder, self).__init__(conf, url_rules, root='', rem_bottom_nav=True)
        self._out_dir = os.path.join(gettempdir(), 'GitBuildingPDF')
        self._stl_page = False
        self._html = {}
        self._installed = 'weasyprint' in sys.modules
        if not self._installed:
            _LOGGER.warning('Trying to build PDF without weasyprint installed')

    def build(self):
        """
        Builds the pdf
        """
        if not self._installed:
            return

        if self._doc.page_order.number_of_paths <= 1:
            if self._doc.page_order.number_of_paths == 1:
                nav_pagelist = self._doc.page_order.nav_pagelists[0]
                page_ordering = buildup_utilities.nav_order_from_nav_pagelist(nav_pagelist)
            else:
                page_ordering = []
            filelist = self.doc.output_files
            self._build_from_filelist('Documentation.pdf', filelist, page_ordering)
        else:
            for n in range(self._doc.page_order.number_of_paths):
                filelist = self._doc.output_for_pathlist(n)
                nav_pagelist = self._doc.page_order.nav_pagelists[n]
                page_ordering = buildup_utilities.nav_order_from_nav_pagelist(nav_pagelist)
                filename = self._get_filename_for_page_ordering(page_ordering)
                subtitle = self._get_subtitle_for_page_ordering(page_ordering)
                self._build_from_filelist(filename, filelist, page_ordering, subtitle=subtitle)

    def _get_filename_for_page_ordering(self, page_ordering):
        rootpage = self._doc.get_page_by_path(page_ordering[0])
        return re.sub(r'[^a-zA-Z0-9\_\-]', '', rootpage.title) + '.pdf'

    def _get_subtitle_for_page_ordering(self, page_ordering):
        rootpage = self._doc.get_page_by_path(page_ordering[0])
        return rootpage.title

    def _build_from_filelist(self, filename, filelist, page_ordering, subtitle=None):

        #temp_dir for html site
        self._make_clean_directory()
        for outfile in filelist:
            #outputs dynamics files to the self.html dictionary
            self._build_file(outfile)
        self._copy_static_files()
        if os.path.exists("assets"):
            self._copy_local_assets()

        combined = ''
        for page in page_ordering:
            combined += self._html[page]
            del self._html[page]
        for page in self._html:
            combined += self._html[page]
        combined = self._renderer.full_pdf(combined, subtitle)
        html_path = os.path.join(self._out_dir, "index.html")
        with open(html_path, 'w') as html_file:
            html_file.write(combined)
        utilities.make_dir_if_needed('_pdf')
        HTML(html_path).write_pdf(os.path.join('_pdf', filename))

    def _build_dynamic_conent(self, outfile, _):
        if not outfile.path.endswith('.md'):
            return
        page_html = self._renderer.render_md(outfile.content,
                                             os.path.splitext(outfile.path)[0],
                                             editorbutton=False,
                                             nav=False,
                                             template=self._renderer.PDFPAGE)
        self._html[outfile.path] = page_html

    def _build_static_conent(self, outfile, full_out_path):
        # Convert all images to a smallish PNG due to GDK_pixbuf bug. Can remove this
        # when upstream bug is fixed
        outpath, ext = os.path.splitext(full_out_path)
        if ext.lower() in ['.jpg', 'jpeg']:
            img = Image.open(outfile.location_on_disk)
            size_tuple = (1000, round(1000*img.size[1]/img.size[0]))
            r_img = img.resize(size_tuple)
            r_img.save(outpath+'.png')
        else:
            super(PdfBuilder, self). _build_static_conent(outfile, full_out_path)
