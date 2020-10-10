"""
{
    'vNID': {
        'anyType': [
            '0105558096348'
        ]
    },
    'vtin': None,
    'vtitleName': {
        'anyType': [
            'บริษัท'
        ]
    },
    'vName': {
        'anyType': [
            'โฟลว์แอคเคาท์ จำกัด'
        ]
    },
    'vSurname': {
        'anyType': [
            '-'
        ]
    },
    'vBranchTitleName': {
        'anyType': [
            'บริษัท'
        ]
    },
    'vBranchName': {
        'anyType': [
            'โฟลว์แอคเคาท์ จำกัด'
        ]
    },
    'vBranchNumber': {
        'anyType': [
            0
        ]
    },
    'vBuildingName': {
        'anyType': [
            'ชุดสกุลไทย สุรวงศ์ ทาวเวอร์'
        ]
    },
    'vFloorNumber': {
        'anyType': [
            '11'
        ]
    },
    'vVillageName': {
        'anyType': [
            '-'
        ]
    },
    'vRoomNumber': {
        'anyType': [
            '12B'
        ]
    },
    'vHouseNumber': {
        'anyType': [
            '141/12'
        ]
    },
    'vMooNumber': {
        'anyType': [
            '-'
        ]
    },
    'vSoiName': {
        'anyType': [
            '-'
        ]
    },
    'vStreetName': {
        'anyType': [
            'สุรวงศ์'
        ]
    },
    'vThambol': {
        'anyType': [
            'สุริยวงศ์'
        ]
    },
    'vAmphur': {
        'anyType': [
            'บางรัก'
        ]
    },
    'vProvince': {
        'anyType': [
            'กรุงเทพมหานคร'
        ]
    },
    'vPostCode': {
        'anyType': [
            '10500'
        ]
    },
    'vBusinessFirstDate': {
        'anyType': [
            '2016/04/07'
        ]
    },
    'vmsgerr': None
}
"""
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import stringcase as stringcase
from loguru import logger


def unnest(soap_data: Dict[str, Optional[Dict[str, List[Union[str, int]]]]], nonull:bool=True):
    # drop none
    if nonull:
        notnull = {k: v for k, v in soap_data.items() if v}

    # anytype flatten
    flatten = {}
    for k, v in notnull.items():
        if k.startswith('v'):
            k = k[1:]
        k = stringcase.snakecase(k)
        try:
            flatten[k] = v['anyType'][0]
            if len(v['anyType']) > 1:
                logger.info(
                    "please let dev. know this case exists. by creating an issue on https://github.com/CircleOnCircles/borisat/issues.")
        except Exception as e:
            logger.exception("unseen format")

    return flatten


def get_error(unnested: Dict[str, Any]) -> Optional[str]:
    """ get error if any"""
    if error_message := unnested.get('msgerr'):
        return error_message
    else:
        return False
