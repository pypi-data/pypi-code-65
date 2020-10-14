import os
import glob
from xml.etree import ElementTree as ET
from distutils.version import LooseVersion
from mcutk.exceptions import ProjectParserError

class SDKManifest(object):
    """NXP MCUXpresso SDK Manifest Parser."""

    @classmethod
    def load_from_dir(cls, sdk_root):
        """Load latest version of manifest from directory."""

        manifestfilelist = glob.glob("{0}/*_manifest*.xml".format(sdk_root))
        if not manifestfilelist:
            raise ProjectParserError("cannot found manifest file")

        if len(manifestfilelist) == 1:
            return SDKManifest(manifestfilelist[0])

        # Find the max version
        file_versions = {}
        for per_file in manifestfilelist:
            version_str = per_file.replace('.xml', '').split('_manifest')[-1]
            version = version_str[1:] if version_str.startswith('_') else version_str
            if version:
                file_versions[version] = per_file

        ver_latest = sorted(file_versions.keys(), key=lambda v: LooseVersion(v))[-1]
        manifest_path = file_versions[ver_latest].replace("\\",'/')

        return SDKManifest(manifest_path)

    def __init__(self, filepath):
        xmlParser = ET.parse(filepath)
        self._xmlroot = xmlParser.getroot()
        self._sdk_root = os.path.dirname(filepath)
        self._id = self._xmlroot.attrib['id']
        self._manifest_version = self._xmlroot.attrib['format_version']
        self._sdk_name = self._xmlroot.attrib["id"]
        self._sdk_version = self._xmlroot.find('./ksdk').attrib['version']

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id
        else:
            return False

    @property
    def id(self):
        return self._id

    @property
    def sdk_version(self):
        return self._sdk_version

    @property
    def sdk_name(self):
        return self._sdk_name

    @property
    def manifest_version(self):
        return self._manifest_version

    def find_example(self, example_id):
        """Return a dict which contain exmaple attributes.

        Keys:
            - id
            - name
            - toolchain
            - brief
            - category
            - path
        """
        xpath = './boards/board/examples/example[@id="{0}"]'.format(example_id)
        example_info = dict()
        node = self._xmlroot.find(xpath)
        if node is None:
            raise Exception("Cannot found example in manifest, id: %s", example_id)

        example_info.update(node.attrib)
        xml_node = node.find('./external[@type="xml"]')
        xml_filename = xml_node.find('./files').attrib['mask']
        example_info['example.xml'] = xml_filename
        return example_info

    @property
    def boards(self):
        xpath = './boards/board'
        nodes = self._xmlroot.findall(xpath)
        return [n.attrib['id'] for n in nodes]

    @property
    def sdk_root(self):
        return self._sdk_root

    def dump_examples(self):
        """Return a list of examples.
        """
        xpath = './boards/board/examples/example'
        examples = list()
        for example_node in self._xmlroot.findall(xpath):
            for toolchain in example_node.attrib['toolchain'].split(" "):
                examples.append({
                    'toolchain': toolchain,
                    'path': example_node.attrib['path'],
                    'name': example_node.attrib['name']
                })
        return examples
