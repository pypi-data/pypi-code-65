def boolean_validator(field, value, error):
    if value and value not in ["true", "false"]:
        error(field, "Must be a boolean value: true or false")


S_ADDRESS_CREATE = {
    "street": {"type": "string"},
    "zip": {"type": "string"},
    "city": {"type": "string"},
    "country": {"type": "string"},
    "state": {"type": "string"},
}

S_ISP_INFO_CREATE = {
    "phone_number": {"type": "string"},
    "type": {"type": "string"},
    "delivery_address": {
        "type": "dict",
        "schema": S_ADDRESS_CREATE
    },
    "previous_provider": {"type": "integer"},
    "previous_owner_vat_number": {"type": "string"},
    "previous_owner_name": {"type": "string"},
    "previous_owner_first_name": {"type": "string"},
}

S_MOBILE_ISP_INFO_CREATE = {
    "icc": {"type": "string"},
    "icc_donor": {"type": "string"},
    "previous_contract_type": {"type": "string"},
}

S_BROADBAND_ISP_INFO_CREATE = {
    "service_address": {
        "type": "dict",
        "schema": S_ADDRESS_CREATE
    },
    "previous_service": {"type": "string"},
    "keep_phone_number": {"type": "boolean"},
    "change_address": {"type": "boolean"},
}

S_CRM_LEAD_RETURN_CREATE = {
    "id": {"type": "integer"}
}

S_CRM_LEAD_CREATE = {
    "name": {"type": "string", "required": True, "empty": False},
    "subscription_request_id": {
        "type": "integer",
        "empty": False,
        "required": True,
        'excludes': ['partner_id'],
    },
    "partner_id": {
        "type": "integer",
        "empty": False,
        "required": True,
        'excludes': ['subscription_request_id'],
    },
    "lead_line_ids": {
        "type": "list",
        "empty": False,
        "schema": {
            "type": "dict",
            "schema": {
                "product_code": {"type": "string", "required": True},
                "name": {"type": "string"},
                "broadband_isp_info": {
                    "type": "dict",
                    # Merging dicts in Python 3.5+
                    # https://www.python.org/dev/peps/pep-0448/
                    "schema": {**S_ISP_INFO_CREATE, **S_BROADBAND_ISP_INFO_CREATE}  # noqa
                },
                "mobile_isp_info": {
                    "type": "dict",
                    "schema": {**S_ISP_INFO_CREATE, **S_MOBILE_ISP_INFO_CREATE}  # noqa
                },
            }
        },
    }
}
S_CONTRACT_SERVICE_INFO_CREATE = {
    "phone_number": {"type": "string", "required": True, "empty": False},
}

S_MOBILE_CONTRACT_SERVICE_INFO_CREATE = {
    "icc": {"type": "string", "required": True, "empty": False},
}
S_ORANGE_ADSL_CONTRACT_SERVICE_INFO_CREATE = {
    "administrative_number": {"type": "string", "required": True, "empty": False},
    "router_product_id": {"type": "integer", "required": True},
    "router_serial_number": {"type": "string", "required": True, "empty": False},
    "router_mac_address": {
        "type": "string", "required": True, "empty": False,
        "regex": "^[0-9A-F]{2}([-:]?)[0-9A-F]{2}(\\1[0-9A-F]{2}){4}$"
    },
    "ppp_user": {"type": "string", "required": True, "empty": False},
    "ppp_password": {"type": "string", "required": True, "empty": False},
    "endpoint_user": {"type": "string", "required": True, "empty": False},
    "endpoint_password": {"type": "string", "required": True, "empty": False},
}

S_VODAFONE_FIBER_CONTRACT_SERVICE_INFO_CREATE = {
    "vodafone_id": {"type": "string", "required": True, "empty": False},
    "vodafone_offer_code": {"type": "string", "required": True, "empty": False},
}

S_ORANGE_FIBER_CONTRACT_SERVICE_INFO_CREATE = {
    "orange_id": {"type": "string", "required": True, "empty": False},
}

S_CONTRACT_CREATE = {
    "name": {"type": "string", "required": True, "empty": False},
    "mobile_contract_service_info": {
        "type": "dict",
        "schema": {
            **S_CONTRACT_SERVICE_INFO_CREATE,
            **S_MOBILE_CONTRACT_SERVICE_INFO_CREATE
        }
    },
    "orange_adsl_contract_service_info": {
        "type": "dict",
        "schema": {
            **S_CONTRACT_SERVICE_INFO_CREATE,
            **S_ORANGE_ADSL_CONTRACT_SERVICE_INFO_CREATE
        }
    },
    "vodafone_fiber_contract_service_info": {
        "type": "dict",
        "schema": {
            **S_CONTRACT_SERVICE_INFO_CREATE,
            **S_VODAFONE_FIBER_CONTRACT_SERVICE_INFO_CREATE
        },
    },
    "orange_fiber_contract_service_info": {
        "type": "dict",
        "schema": {
            **S_CONTRACT_SERVICE_INFO_CREATE,
            **S_ORANGE_FIBER_CONTRACT_SERVICE_INFO_CREATE,
        }
    },
    "partner_id": {"type": "integer", "required": True},
    "service_partner_id": {"type": "integer", "required": False},
    "service_technology": {
        "type": "string", "required": True, "empty": False,
        'anyof': [
            {'allowed': ['Mobile'], 'allof': [
                {'dependencies': {'service_supplier': 'Másmóvil'}},
                {'dependencies': ['mobile_contract_service_info']},
            ]},
            {'allowed': ['Fiber'], 'anyof': [
                {'allof': [
                    {'dependencies': {'service_supplier': 'Vodafone'}},
                    {'dependencies': ['vodafone_fiber_contract_service_info']}
                ]},
                {'allof': [
                    {'dependencies': {'service_supplier': 'Orange'}},
                    {'dependencies': ['orange_fiber_contract_service_info']}
                ]}
            ]},
            {'allowed': ['ADSL'], 'allof':[
                {'dependencies': ['orange_adsl_contract_service_info']},
                {'dependencies': {'service_supplier': 'Orange'}},
            ]}
        ]
    },
    "service_supplier": {"type": "string", "required": True, "empty": False},
    "contract_lines": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "product_code": {"type": "string", "required": True},
            }
        }
    }
}

S_CONTRACT_RETURN_CREATE = {
    "id": {"type": "integer"}
}

S_PREVIOUS_PROVIDER_REQUEST_SEARCH = {
    "mobile": {"type": "string", "check_with": boolean_validator},
    "broadband": {"type": "string", "check_with": boolean_validator},
}

S_PREVIOUS_PROVIDER_RETURN_SEARCH = {
    "count": {"type": "integer"},
    "providers": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "id": {"type": "integer", "required": True},
                "name": {"type": "string", "required": True},
            }
        }
    }
}
