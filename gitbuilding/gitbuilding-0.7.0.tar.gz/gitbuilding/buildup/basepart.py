'''
This submodule contains functionality to handle parts in the BuildUp documentation.
'''
from copy import copy
import logging
from gitbuilding.buildup.link import BaseLink, make_link
from gitbuilding.buildup.quantity import zero_quantity

_LOGGER = logging.getLogger('BuildUp')
class Part:
    """
    A part is anything that can be counted in the documentation. This includes
    componets and tools that are used (UsedParts). And other parts created in
    a page (CreatedPart).
    """

    def __init__(self, link):
        self._name = link.linktext
        #Storing all links and calculate parts like the category on the fly.
        self._links = []
        self.count(link)

    def replicate(self):
        """
        Returns a repliclica of this part.
        """
        # pylint: disable=protected-access
        replica = copy(self)
        replica._links = copy(self._links)
        return replica

    @property
    def _all_locations(self):
        locations = []
        for link in self._links:
            if not link.location_undefined:
                locations.append(link.link_rel_to_root)
        return locations

    @property
    def _all_alttexts(self):
        alttexts = []
        for link in self._links:
            if link.alttext != '':
                alttexts.append(link.alttext)
        return alttexts

    @property
    def _all_qtys(self):
        qtys = []
        for link in self._links:
            if link.buildup_data.qty is not None:
                qtys.append(link.buildup_data.qty)
        return qtys

    @property
    def name(self):
        """
        Read-only property: The name of the part. This is equivalent to
        the text of the link in the build up.
        """
        return self._name

    @property
    def qty(self):
        """
        Read-only property: The total quantity of this part used in references
        in the text. This differs from total_qty as total_qty can be set explicitly.
        If total_qty is not set then total_qty will be set equal to qty. If
        total_qty is set and doesn't match qty a warning will be logged.
        """

        all_qtys = self._all_qtys
        if len(all_qtys) > 0:
            qty = sum(all_qtys, zero_quantity())
        else:
            qty = None
        return qty

    def get_links(self):
        """
        Returns the list of links that define this part
        """
        return self._links

    @property
    def linklocation(self):
        """
        Read-only property: The URL for the part relative to the root of the
        directory
        """
        locations = self._all_locations
        if len(locations) > 0:
            return locations[0]
        return ''

    @property
    def alttext(self):
        """
        Read-only property: The alttext for the part
        """
        alttexts = self._all_alttexts
        if len(alttexts) > 0:
            return ' '.join(alttexts)
        return ''

    @property
    def location_undefined(self):
        """
        Boolean read-only property True if no URL is defined.
        """
        return self.linklocation == ''

    def link_ref_md(self, url_translator):
        """
        Returns the markdown link reference for this part.
        """
        link_dict = {"fullmatch": None,
                     "linktext": self.name,
                     "linklocation": self.linklocation,
                     "alttext": self.alttext,
                     "buildup_data": None}
        #make a link object relative to root
        link_obj = make_link(link_dict, 'index.md')
        return link_obj.link_ref_md(url_translator)

    def __eq__(self, obj):
        """
        Two parts are considered equal if their names match. This allows use of
        inbuilt methods such as "in" and "index". A string or link will also compare
        to the part name.
        """

        if isinstance(obj, str):
            return obj == self.name
        if isinstance(obj, BaseLink):
            return obj.linktext == self.name
        if isinstance(obj, Part):
            return obj.name == self.name
        return NotImplemented

    def count(self, link):
        """
        Counts more of the same parts on a page..
        """
        checks = [self._check_link_location]
        self._count(link, checks)


    def _count(self, link, checks):
        if not isinstance(link, BaseLink):
            raise TypeError('Part.count expects a Link object')
        if link.linktext != self.name:
            raise ValueError(f'Cannot count the link as the linktext "{link.linktext}"'
                             f'does not equal the partname "{self.name}"')
        for check in checks:
            check(link)
        self._links.append(link)

    def _check_link_location(self, link):
        if not link.location_undefined:
            locations = self._all_locations
            if len(locations) > 0 and link.link_rel_to_root != locations[0]:
                _LOGGER.warning('Location multiply defined on this page for %s', self.name)
