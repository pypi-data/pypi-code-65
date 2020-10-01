# coding: utf-8

"""
    Pulp 3 API

    Fetch, Upload, Organize, and Distribute Software Packages  # noqa: E501

    The version of the OpenAPI document: v3
    Contact: pulp-list@redhat.com
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest
import datetime

import pulpcore.client.pulp_ansible
from pulpcore.client.pulp_ansible.models.ansible_collection_version_response import AnsibleCollectionVersionResponse  # noqa: E501
from pulpcore.client.pulp_ansible.rest import ApiException

class TestAnsibleCollectionVersionResponse(unittest.TestCase):
    """AnsibleCollectionVersionResponse unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test AnsibleCollectionVersionResponse
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = pulpcore.client.pulp_ansible.models.ansible_collection_version_response.AnsibleCollectionVersionResponse()  # noqa: E501
        if include_optional :
            return AnsibleCollectionVersionResponse(
                pulp_created = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                artifact = '0', 
                pulp_href = '0', 
                md5 = '0', 
                sha1 = '0', 
                sha224 = '0', 
                sha256 = '0', 
                sha384 = '0', 
                sha512 = '0', 
                id = '0', 
                authors = [
                    '0'
                    ], 
                contents = [
                    None
                    ], 
                dependencies = None, 
                description = '0', 
                docs_blob = None, 
                documentation = '0', 
                homepage = '0', 
                issues = '0', 
                license = [
                    '0'
                    ], 
                name = '0', 
                namespace = '0', 
                repository = '0', 
                tags = [
                    pulpcore.client.pulp_ansible.models.ansible/tag_response.ansible.TagResponse(
                        name = '0', )
                    ], 
                version = '0', 
                deprecated = True
            )
        else :
            return AnsibleCollectionVersionResponse(
                artifact = '0',
                id = '0',
                authors = [
                    '0'
                    ],
                contents = [
                    None
                    ],
                dependencies = None,
                description = '0',
                docs_blob = None,
                documentation = '0',
                homepage = '0',
                issues = '0',
                license = [
                    '0'
                    ],
                name = '0',
                namespace = '0',
                repository = '0',
                version = '0',
        )

    def testAnsibleCollectionVersionResponse(self):
        """Test AnsibleCollectionVersionResponse"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
