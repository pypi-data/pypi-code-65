import json
import odoo

from odoo.addons.easy_my_coop_api.tests.common import BaseEMCRestCase

HOST = "127.0.0.1"
PORT = odoo.tools.config["http_port"]


class BaseEMCRestCaseAdmin(BaseEMCRestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        # Skip parent class in super to avoid recreating api key
        super(BaseEMCRestCase, cls).setUpClass(*args, **kwargs)
        cls.AuthApiKey = cls.env["auth.api.key"]
        admin = cls.env.ref("base.user_admin")
        cls.api_key_test = cls.AuthApiKey.create(
            {"name": "test-key", "key": "api-key", "user_id": admin.id}
        )


class TestContractController(BaseEMCRestCaseAdmin):

    def setUp(self):
        super().setUp()
        self.router_product = self.env['product.product'].create({
            'name': 'Router',
            'categ_id': self.ref('somconnexio.router_category'),
            'tracking': 'serial'
        })

    def http_public_post(self, url, data, headers=None):
        if url.startswith("/"):
            url = "http://{}:{}{}".format(HOST, PORT, url)
        return self.session.post(url, json=data)

    def test_route_right_create(self):
        url = "/public-api/contract"
        data = {
            "name": "123456",
            "partner_id": self.ref('base.res_partner_12'),
            "service_technology": 'Mobile',
            "service_supplier": "Másmóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.reason, "OK")
        content = json.loads(response.content.decode("utf-8"))
        self.assertIn('id', content)
        contract = self.env['contract.contract'].browse(content['result']['id'])
        self.assertEquals(contract.name, data['name'])
        self.assertEquals(
            contract.partner_id,
            self.browse_ref('base.res_partner_12')
        )
        self.assertEquals(
            contract.invoice_partner_id,
            self.browse_ref('base.res_partner_12')
        )
        self.assertEquals(
            contract.service_technology_id,
            self.browse_ref('somconnexio.service_technology_mobile')
        )
        self.assertEquals(
            contract.service_supplier_id,
            self.browse_ref('somconnexio.service_supplier_masmovil')
        )
        self.assertTrue(
            contract.mobile_contract_service_info_id
        )
        self.assertEquals(
            contract.mobile_contract_service_info_id.icc,
            data['mobile_contract_service_info']['icc']
        )
        self.assertEquals(
            contract.mobile_contract_service_info_id.phone_number,
            data['mobile_contract_service_info']['phone_number']
        )

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_partner_create(self):
        url = "/public-api/contract"
        data = {
            "name": "123456",
            "partner_id": 666,
            "service_technology": 'Mobile',
            "service_supplier": "Másmóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.reason,
                          str("Partner id 666 not found".encode('utf-8'))
                          )

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_tech_create(self):
        url = "/public-api/contract"
        data = {
            "name": "123456",
            "partner_id": self.ref('base.res_partner_12'),
            "service_technology": 'XXXX',
            "service_supplier": "Másmóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 400)
        self.assertIn(
            "unallowed value XXXX",
            response.reason
        )

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_supplier_create(self):
        url = "/public-api/contract"
        data = {
            "name": "123456",
            "partner_id": self.ref('base.res_partner_12'),
            "service_technology": 'Mobile',
            "service_supplier": "XXXX",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 400)
        self.assertIn(
            "no definitions validate",
            response.reason
        )

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_combination_create(self):
        url = "/public-api/contract"
        data = {
            "name": "123456",
            "partner_id": self.ref('base.res_partner_12'),
            "service_technology": 'Fiber',
            "service_supplier": "Másmóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 400)
        self.assertIn(
            "no definitions validate",
            response.reason
        )

    def test_route_right_contract_lines(self):
        url = "/public-api/contract"
        data = {
            "name": "123456",
            "partner_id": self.ref('base.res_partner_12'),
            "service_technology": 'Mobile',
            "service_supplier": "Másmóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [
                {
                    "product_code": (
                        self.browse_ref('somconnexio.100Min1GB').default_code
                    ),
                },
                {
                    "product_code": (
                        self.browse_ref('somconnexio.EnviamentSIM').default_code
                    ),
                }
            ]
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.reason,
                          "OK"
                          )
        content = json.loads(response.content.decode("utf-8"))
        self.assertIn('id', content)
        contract = self.env['contract.contract'].browse(content['result']['id'])
        self.assertEquals(contract.name, data['name'])
        self.assertEquals(
            contract.partner_id,
            self.browse_ref('base.res_partner_12')
        )
        self.assertEquals(
            contract.invoice_partner_id,
            self.browse_ref('base.res_partner_12')
        )
        self.assertEquals(
            contract.service_technology_id,
            self.browse_ref('somconnexio.service_technology_mobile')
        )
        self.assertEquals(
            contract.service_supplier_id,
            self.browse_ref('somconnexio.service_supplier_masmovil')
        )
        self.assertIn(
            self.browse_ref('somconnexio.100Min1GB'), [
                c.product_id
                for c in contract.contract_line_ids
            ]
        )
        self.assertIn(
            self.browse_ref('somconnexio.EnviamentSIM'), [
                c.product_id
                for c in contract.contract_line_ids
            ]
        )

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_product_id(self):
        url = "/public-api/contract"
        data = {
            "name": "123456",
            "partner_id": self.ref('base.res_partner_12'),
            "service_technology": 'Mobile',
            "service_supplier": "Másmóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [
                {
                    "product_code": (
                        self.browse_ref('somconnexio.100Min1GB').default_code
                    ),
                },
                {
                    "product_code": "SC_0",
                }
            ]
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.reason,
                          str("Product with code SC_0 not found".encode('utf-8'))
                          )

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_format_product(self):
        url = "/public-api/contract"
        data = {
            "name": "123456",
            "partner_id": self.ref('base.res_partner_12'),
            "service_technology": 'Mobile',
            "service_supplier": "Másmóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [
                {
                    "product_code": (
                        self.browse_ref('somconnexio.100Min1GB').default_code
                    ),
                },
                {
                    "product_code": 666,
                }
            ]
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.reason,
                          str((
                              "Bad format - {'contract_lines': "
                              "[{1: [{'product_code': "
                              "['must be of string type']}]}]}"
                              ).encode('utf-8'))
                          )

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_mobile_missing_icc(self):
        url = "/public-api/contract"
        data = {
            "name": "123456",
            "partner_id": self.ref('base.res_partner_12'),
            "service_technology": 'Mobile',
            "service_supplier": "Másmóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
            },
            "contract_lines": [],
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 400)
        self.assertIn("'icc': ['required field']", response.reason)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_mobile_missing_phone_number(self):
        url = "/public-api/contract"
        data = {
            "name": "123456",
            "partner_id": self.ref('base.res_partner_12'),
            "service_technology": 'Mobile',
            "service_supplier": "Másmóvil",
            "mobile_contract_service_info": {
                "icc": "123456",
            },
            "contract_lines": [],
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 400)
        self.assertIn("'phone_number': ['required field']", response.reason)

    def test_route_right_adsl(self):
        url = "/public-api/contract"
        data = {
            "name": "123456",
            "partner_id": self.ref('base.res_partner_12'),
            "service_partner_id": self.ref('base.res_partner_12'),
            "service_technology": 'ADSL',
            "service_supplier": "Orange",
            "orange_adsl_contract_service_info": {
                "phone_number": "654123456",
                'administrative_number': '123',
                'router_product_id': self.router_product.id,
                'router_serial_number': '4637',
                'router_mac_address': 'AA:BB:CC:22:33:11',
                'ppp_user': 'ringo',
                'ppp_password': 'rango',
                'endpoint_user': 'connection',
                'endpoint_password': 'password'
            },
            "contract_lines": [],
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.reason,
                          "OK"
                          )
        content = json.loads(response.content.decode("utf-8"))
        self.assertIn('id', content)
        contract = self.env['contract.contract'].browse(content['result']['id'])
        self.assertTrue(contract.orange_adsl_service_contract_info_id)
        contract_service_info = contract.orange_adsl_service_contract_info_id
        self.assertEquals(contract_service_info.phone_number, '654123456')
        self.assertEquals(contract_service_info.administrative_number, '123')
        self.assertEquals(
            contract_service_info.router_lot_id.product_id.id,
            self.router_product.id
        )
        self.assertEquals(
            contract_service_info.router_lot_id.name,
            '4637'
        )
        self.assertEquals(
            contract_service_info.router_lot_id.router_mac_address,
            'AA:BB:CC:22:33:11'
        )
        self.assertEquals(
            contract_service_info.ppp_user,
            'ringo'
        )
        self.assertEquals(
            contract_service_info.ppp_password,
            'rango'
        )
        self.assertEquals(
            contract_service_info.endpoint_user,
            'connection'
        )
        self.assertEquals(
            contract_service_info.endpoint_password,
            'password'
        )

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_mac_address(self):
        url = "/public-api/contract"
        data = {
            "name": "123456",
            "partner_id": self.ref('base.res_partner_12'),
            "service_partner_id": self.ref('base.res_partner_12'),
            "service_technology": 'ADSL',
            "service_supplier": "Orange",
            "orange_adsl_contract_service_info": {
                "phone_number": "654123456",
                'administrative_number': '123',
                'router_product_id': self.router_product.id,
                'router_serial_number': '4637',
                'router_mac_address': 'AA:BB:CC:22:33:XX',
                'ppp_user': 'ringo',
                'ppp_password': 'rango',
                'endpoint_user': 'connection',
                'endpoint_password': 'password'
            },
            "contract_lines": [],
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 400)
        self.assertIn(
            'value does not match regex',
            response.reason
        )

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_router_product_id(self):
        url = "/public-api/contract"
        data = {
            "name": "123456",
            "partner_id": self.ref('base.res_partner_12'),
            "service_partner_id": self.ref('base.res_partner_12'),
            "service_technology": 'ADSL',
            "service_supplier": "Orange",
            "orange_adsl_contract_service_info": {
                "phone_number": "654123456",
                'administrative_number': '123',
                'router_product_id': 0,
                'router_serial_number': '4637',
                'router_mac_address': 'AA:BB:CC:22:33:44',
                'ppp_user': 'ringo',
                'ppp_password': 'rango',
                'endpoint_user': 'connection',
                'endpoint_password': 'password'
            },
            "contract_lines": [],
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(
            str('No router product id for 0'.encode('utf-8')),
            response.reason
        )

    def test_route_right_vodafone_fiber(self):
        url = "/public-api/contract"
        data = {
            "name": "123456",
            "partner_id": self.ref('base.res_partner_12'),
            "service_partner_id": self.ref('base.res_partner_12'),
            "service_technology": 'Fiber',
            "service_supplier": "Vodafone",
            "vodafone_fiber_contract_service_info": {
                "phone_number": "654123456",
                'vodafone_offer_code': 'offer',
                'vodafone_id': "123"
            },
            "contract_lines": [],
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.reason,
                          "OK"
                          )
        content = json.loads(response.content.decode("utf-8"))
        self.assertIn('id', content)
        contract = self.env['contract.contract'].browse(content['result']['id'])
        self.assertTrue(contract.vodafone_fiber_service_contract_info_id)
        contract_service_info = contract.vodafone_fiber_service_contract_info_id
        self.assertEquals(contract_service_info.phone_number, '654123456')
        self.assertEquals(contract_service_info.vodafone_id, '123')
        self.assertEquals(contract_service_info.vodafone_offer_code, 'offer')

    def test_route_right_orange_fiber(self):
        url = "/public-api/contract"
        data = {
            "name": "123456",
            "partner_id": self.ref('base.res_partner_12'),
            "service_partner_id": self.ref('base.res_partner_12'),
            "service_technology": 'Fiber',
            "service_supplier": "Orange",
            "orange_fiber_contract_service_info": {
                "phone_number": "654123456",
                'orange_id': "123"
            },
            "contract_lines": [],
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.reason,
                          "OK"
                          )
        content = json.loads(response.content.decode("utf-8"))
        self.assertIn('id', content)
        contract = self.env['contract.contract'].browse(content['result']['id'])
        self.assertTrue(contract.orange_fiber_service_contract_info_id)
        contract_service_info = contract.orange_fiber_service_contract_info_id
        self.assertEquals(contract_service_info.phone_number, '654123456')
        self.assertEquals(contract_service_info.orange_id, '123')
