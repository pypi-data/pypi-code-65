import http
from string import Template

from easyqueue.utils.validation import TypeValidator

from easyqueue.client.base_client import BaseClient
from easyqueue.enums.RestHeaders import RestHeaders
from easyqueue.enums.RestMethods import RestMethods


class EQObjectClient(BaseClient):

    __context_path = 'eqobject'
    __status_health_template = Template('$protocol://$hostport/$path/api/status/health')
    __eqobject_crud_one_template = Template('$protocol://$hostport/$path/api/eqobject/$identification')
    __eqobject_crud_many_template = Template('$protocol://$hostport/$path/api/eqobject/')

    @staticmethod
    def __get_default_headers():
        return {
            RestHeaders.ACCEPT_STR.value: RestHeaders.APP_JSON.value,
            RestHeaders.CONT_TYPE.value: RestHeaders.APP_JSON.value
        }

    def health(self):
        result = None
        url = self.__status_health_template.substitute(
            protocol=self.protocol, hostport=self.hostport, path=self.__context_path)
        headers = self.__get_default_headers()
        response = self.call(method=RestMethods.GET.value, url=url, headers=headers)

        if response.status_code == http.HTTPStatus.OK:
            result = response.json()
            self.add_to_debug_trace('Health check successfully: {}'.format(result))
        else:
            self.add_to_debug_trace('Not possible to health check: {} - {}'.format(response.status_code, response.text))

        return result

    def create_one(self, identification, element):
        result = None
        TypeValidator.raise_validation_element_type(
            element_name='element', element=element, type_class=dict, allow_none=False)
        element['identification'] = identification
        url = self.__eqobject_crud_one_template.substitute(
            protocol=self.protocol, host=self.hostport, path=self.__context_path, identification=identification)
        headers = self.__get_default_headers()
        response = self.call(method=RestMethods.POST.value, url=url, headers=headers, body=element)

        if response.status_code == http.HTTPStatus.OK:
            result = response.json()
            self.add_to_debug_trace('Operation "create_one" successfully: {}'.format(result))
        else:
            self.add_to_debug_trace('Error in operation "create_one": {} - {}'.format(response.status_code, response.text))

        return result

    def create_many(self, elements):
        result = None
        TypeValidator.raise_validation_element_type(
            element_name='elements', element=elements, type_class=list, allow_none=False)
        url = self.__eqobject_crud_many_template.substitute(
            protocol=self.protocol, host=self.hostport, path=self.__context_path)
        headers = self.__get_default_headers()
        response = self.call(method=RestMethods.POST.value, url=url, headers=headers, body=elements)

        if response.status_code == http.HTTPStatus.OK:
            result = response.json()
            self.add_to_debug_trace('Operation "create_many" successfully: {}'.format(result))
        else:
            self.add_to_debug_trace('Error in operation "create_many": {} - {}'.format(response.status_code, response.text))

        return result
