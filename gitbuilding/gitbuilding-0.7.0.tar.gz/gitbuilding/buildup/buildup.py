"""
The main submodule for parsing BuildUp. This constains both the BuildUpParser class
and classes Links and Images. It also contains the function that parses the inline
part data.
"""

import re
import logging

from gitbuilding.buildup.link import make_link, BaseLink, Image
from gitbuilding.buildup.utilities import clean_id

_LOGGER = logging.getLogger('BuildUp')

IMAGE_REGEX = r'(!\[([^\]]*)\]\(\s*([^\)\n\r\t\"]+?)\s*(?:\"([^\"\n\r]*)\")?\s*\))'
LINK_REGEX = (r'(?<!\!)(\[([^\[\]\n\r]+?)\](?:\(\s*(\S+)\s*(?:\"([^\"\n\r]*)\")?\s*\))?'
              r"""(?:{([^:\n\r](?:[^}\'\"\n\r]|\"[^\"\r\n]*\"|\'[^\'\r\n]*\')*)})?)""")

def _process_value(value):
    if value is not None:
        #if not none it is a string.
        #Strip any whitespace from either end
        value = value.strip()
        if value.startswith(("'", '"')):
            #remove quotes from quoted values
            value = value[1:-1]
        elif value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
    return value

def parse_inline_data(data):
    """
    Parses the inline key:value pair data. Keys are either strings or boolean
    set with the string "true" or "false" (case insensitive). To set the literal
    string true or false put the value in quotes. Keys are case insensive and can
    only contain the caracters a-z. Cannot contain any of { } : , " '
    To use these character you will need to put the value in single or double
    quotes.
    The keys "step" and "ouput" return True if they are entered with no value.
    """

    empty_is_true = ['step', 'output', 'bom']
    if data in [None, '']:
        return None

    # This regex finds a key value pair at the start of the data string
    # the pair ends in the end of the string or a comma
    # The key can is case insensitve and can only be the letters a-z or _
    # The value cannot contain { } : , " '
    # To use these characters the value should be in quotes
    reg = re.compile(r'^\s*([a-zA-Z_]+)(?:\s*:\s*'
                     r'''([^{}:,\n\r\"\']*|\"[^\n\r\"]*\"|\'[^\n\r\']*\'))?'''
                     r'\s*(?:$|,)')
    data_dict = {}
    alldata = data
    while len(data.lstrip()) > 0:
        match = reg.match(data)
        if match is None:
            _LOGGER.warning("Cannot parse the buildup data %s.", alldata)
            return None
        key = match.group(1).lower()
        value = _process_value(match.group(2))
        if key in empty_is_true and value is None:
            value = True
        data_dict[key] = value
        data = data[match.end(0):]
    if data_dict == {}:
        return None
    return data_dict

class BuildUpParser():
    """
    This is main parser for reading the buildup.
    It is not really a parser, it is just about 8 or so regexs that find the BuildUp
    specific syntax.
    An object is initialised with the raw text to parse, the directory of the page the
    text is from so that the any relative links can be translated
    """

    def __init__(self, raw_text, page_path):

        self._raw_text = raw_text
        self._page_path = page_path
        self._link_refs = []
        self._buildup_links = []
        self._images = []
        self._plain_links = []

        self._find_links()

    @property
    def link_refs(self):
        """
        Returns a list of Link objects, one for each link reference in the page
        """
        return self._link_refs

    @property
    def step_links(self):
        """
        Returns a list of Link objects, one for each link to a step on the page
        """
        return [link for link in self._buildup_links if link.is_step]

    @property
    def part_links(self):
        """
        Returns a list of Link objects, one for each inline part link on the page
        """
        return [link for link in self._buildup_links if link.is_part]

    @property
    def outputs(self):
        """
        Returns a list of Link objects, one for each output from the parsed page
        """
        return [link for link in self._buildup_links if link.is_output]

    @property
    def bom_links(self):
        """
        Returns a list of Link objects, one for each output from the parsed page
        """
        return [link for link in self._buildup_links if link.is_bom]

    @property
    def images(self):
        """
        Returns a list of Image objects, one for each image
        """
        return self._images

    @property
    def plain_links(self):
        """
        Returns a list of Link objects, one for each link that is not a build up link
        """
        return self._plain_links

    @property
    def all_links(self):
        """
        Returns a list of Link objects, one for each link in the page.
        Doesn't return images. See all_links_and_images()
        """
        return self._plain_links+self._buildup_links

    @property
    def all_links_and_images(self):
        """
        Returns a list of Link and Image objects, one for each link/image
        in the page.
        """
        return self.all_links+self.images

    @property
    def in_page_steps(self):
        """
        Returns the in-page steps for your page in a dictionary with:
        heading, id, fullmatch
        """
        return self._get_in_page_steps()

    @property
    def steps(self):
        """
        Returns a simple list of the filespaths of all pages linked to a steps
        """
        return [link.link_rel_to_root for link in self.step_links]

    @property
    def inline_boms(self):
        """
        Returns a list of each fullmatch of the syntax for an in-line bill of materials
        """
        return re.findall(r"(\{\{[ \t]*BOM[ \t]*\}\})", self._raw_text, re.MULTILINE)

    @property
    def bom_links_dep(self):
        """
        Returns a list of each fullmatch of the syntax for an in-line bill of materials
        """
        bomlinks = re.findall(r"(\{\{[ \t]*BOMlink[ \t]*\}\})", self._raw_text, re.MULTILINE)
        if len(bomlinks) > 0:
            _LOGGER.warning('Depreciation warning. The {{BOMlink}} syntax has been replaced by'
                            ' appending {bom} to a link.')
        return bomlinks

    @property
    def reference_defined_parts(self):
        """
        Returns a list of link objets for the parts defined by references
        """
        list_of_parts = []
        for link_ref in self._link_refs:
            if link_ref.is_part:
                list_of_parts.append(link_ref)
        return list_of_parts

    @property
    def inline_parts(self):
        """
        Returns a list of link objects for the parts defined inline
        """
        list_of_parts = []
        for part_link in self.part_links:
            list_of_parts.append(part_link)
        return list_of_parts

    def get_title(self):
        """
        Gets the page title by looking for the first heading with a single #
        """
        return self._match_title()[1]

    def get_title_match(self):
        """
        Gets the match to page title by looking for the first heading with a
        single #
        """
        return self._match_title()[0]

    def _match_title(self):
        headings = re.findall(r"(^#(?!#)[ \t]*(.*)$)",
                              self._raw_text,
                              re.MULTILINE)
        if len(headings) > 0:
            title = headings[0]
        else:
            title = ("", "")
        return title

    def _find_links(self):
        self._link_refs = self._get_link_references()
        self._buildup_links, self._plain_links = self._get_links()
        self._images = self._get_images()

    def _get_link_references(self):
        """
        Function to find link reference of any reference style links.
        Returns a list of Link objects
        """

        # Looking for link references. These must use "*" or '*' to define alt-text not (*)
        # Group 1: link text
        # Group 2: link location
        # Group 3: either a ' or a ", captured so regex can find the equivalent
        # Group 4: alt text
        link_ref_matches = re.findall(r"""(^[ \t]*\[(.+)\]:[ \t]*([^\"\' \t\n\r]*)"""
                                      r"""(?:[ \t]+(\"|')((?:\\\4|(?!\4).)*?)\4)?[ \t]*$)""",
                                      self._raw_text,
                                      re.MULTILINE)

        link_refs = []
        for link_ref in link_ref_matches:
            alttext = link_ref[4]
            # Search for buildup data in alt-text
            data_match = re.findall(r"""({([^:](?:[^}\'\"]|\'[^\'\r\n]*\')*)})""",
                                    alttext)
            if len(data_match) == 0:
                buildup_data = None
            else:
                if len(data_match) > 1:
                    _LOGGER.warning("Multiple sets of data found in link reference alt-text: %s",
                                    alttext)
                # Only match the last group of data found, warning if more than one
                # buildup_data is the text inside braces
                buildup_data = data_match[-1][1]
                # Replace all including braces
                alttext = alttext.replace(data_match[-1][0], "")
            if link_ref[2] == "":
                location = ""
            else:
                location = link_ref[2]
            link_ref_dict = {"fullmatch": link_ref[0],
                             "linktext": link_ref[1],
                             "linklocation": location,
                             "alttext": alttext,
                             "buildup_data": parse_inline_data(buildup_data)}
            link_refs.append(make_link(link_ref_dict,
                                       self._page_path,
                                       link_type=BaseLink.LINK_REF))

        return link_refs


    def _get_links(self):
        """
        Function to find all markdown links
        Returns two list of Link objects
        The first is a list of buildup links (links with {} after them)
        The second is a list of plain markdown links
        """

        buildup_links = []
        plain_links = []
        link_matches = re.findall(LINK_REGEX,
                                  self._raw_text,
                                  re.MULTILINE)

        for link in link_matches:
            if link[2] == "":
                linklocation = ""
            else:
                linklocation = link[2]
            link_dict = {"fullmatch": link[0],
                         "linktext": link[1],
                         "linklocation": linklocation,
                         "alttext": link[3],
                         "buildup_data": parse_inline_data(link[4])}
            link_obj = make_link(link_dict,
                                 self._page_path,
                                 link_references=self._link_refs)
            if link_obj.buildup_data is None:
                plain_links.append(link_obj)
            else:
                buildup_links.append(link_obj)
        return buildup_links, plain_links

    def _get_images(self):
        """
        Function to find images
        Returns a list of Image objects
        """

        # Find images in the text
        # Group 1: all
        # Group 2: alt-text
        # Group 3: image-path
        # group 4: hover text
        images_info = re.findall(IMAGE_REGEX,
                                 self._raw_text,
                                 re.MULTILINE)

        images = []
        for image in images_info:
            image_location = image[2]
            image_dict = {"fullmatch": image[0],
                          "alttext": image[1],
                          "imagelocation": image_location,
                          "hovertext": image[3]}
            images.append(Image(image_dict,
                                self._page_path,
                                link_references=self._link_refs))
        return images

    def _get_in_page_steps(self):
        """
        Returns h2 headings with data info afterwards. Used to locate page steps.
        """

        in_page_steps = []
        step_ids = []

        # regex:
        # Group 1 (heading[0]) Full match
        # Group 2 (heading[1]) is the heading text
        # Group 3 (heading[2]) is the inline buildup data
        headings = re.findall(r"^(##(?!#)[ \t]*(.*?)[ \t]*{([^:][^}\n]*)})$",
                              self._raw_text,
                              re.MULTILINE)

        for heading in headings:
            heading_info = parse_inline_data(heading[2])

            if "pagestep" in heading_info:
                step_id = heading_info["pagestep"]
                if step_id is None:
                    step_id = clean_id(heading[1])
                elif clean_id(step_id) != step_id:
                    old_id = step_id
                    step_id = clean_id(step_id)
                    _LOGGER.warning('Step ID "%s" not valid, changed to "%s"', old_id, step_id)

                if step_id not in step_ids:
                    step_ids.append(step_id)
                else:
                    _LOGGER.warning('Step ID "%s" is already used', step_id)
                in_page_steps.append({"heading": heading[1],
                                      "id": step_id,
                                      "fullmatch": heading[0]})
                del heading_info["pagestep"]

            if len(heading_info.keys()) > 0:
                keynames = ""
                for key in heading_info:
                    keynames += key + ", "
                _LOGGER.warning("Unused keys '%s' in heading [%s]",
                                keynames[:-2],
                                heading[1],
                                extra={'fussy':True})
        return in_page_steps
