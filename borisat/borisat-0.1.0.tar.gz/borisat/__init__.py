from typing import Optional

from loguru import logger
from pydantic import constr
from pydantic import validate_arguments

from borisat.apis.rd import call
from borisat.apis.rd import call_service
from borisat.apis.rd import get_client
from borisat.models.rd.unnested import get_error
from borisat.models.rd.vat import CompanyInfoResponse
from borisat.models.rd.unnested import unnest


@validate_arguments
def get_info(
        tax_id: Optional[constr(min_length=13, max_length=13)]=None,
        name: Optional[str]=None,
        branch_number: int=0
) -> Optional[CompanyInfoResponse]:

    result = call(tax_id, name, 0, branch_number, 0, wsdl='https://rdws.rd.go.th/serviceRD3/vatserviceRD3.asmx?wsdl')

    unnested = unnest(result)
    if error := get_error(unnested):
        logger.error(error)
        return None
    else:
        return CompanyInfoResponse(**unnested)


@validate_arguments
def is_exist(
        tax_id: constr(min_length=13, max_length=13) = None,
) -> Optional[CompanyInfoResponse]:
    result = call(tax_id,
                  wsdl='https://rdws.rd.go.th/serviceRD3/checktinpinservice.asmx?wsdl')

    unnested = unnest(result)
    if unnested.get('is_exist') == 'Yes':
        return True
    else:
        return False
