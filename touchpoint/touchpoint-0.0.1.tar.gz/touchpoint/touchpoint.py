import json

import requests

class Touchpoint():
    from .employee import Employee
    from .location import Location
    from .item import Item

    def __init__(self, api_key=None):
        if api_key is None:
            raise ValueError("A valid API_KEY must be provided.")
        self.api_key = api_key

    @classmethod
    def url(cls, path='/', pretty=False):
        base_url = 'http://c1.tchpt.com'
        query = ['?']
        if pretty:
            query.append('pretty=1')

        req_url = base_url + path + ''.join(query)
        return req_url

    def _headers(self):
        return {'content-type': 'application/json',
                'Api-Key': self.api_key}

    def ping(self):
        req = requests.get(self.url('/api/ping'))
        return req.status_code

    def ping_full(self):
        req = requests.get(self.url('/api/ping'))
        return req.text

    # Fetch all employees
    def get_employees(self, store_id=None):
        employees = []
        path = f'/api/location/{store_id}/employees'

        req = requests.get(self.url(path, pretty=True), headers=self._headers())

        employees_data = json.loads(req.text)

        for emp in employees_data['data']['employees']:
            employees.append(self.Employee(employee_id=emp['id'],
                                           first_name=emp['firstname'],
                                           last_name=emp['lastname'],
                                           emp_id=emp['emp_id']))
        return employees

    # Fetch an employee
    def get_employee(self, store_id=None, employee_id=None):
        path = f'/api/location/{store_id}/employees/{employee_id}'
        req = requests.get(self.url(path, pretty=True), headers=self._headers())

        employee_data = json.loads(req.text)

        emp = employee_data['data']['employees'][0]

        return self.Employee(employee_id=emp['id'],
                             first_name=emp['firstname'],
                             last_name=emp['lastname'],
                             emp_id=emp['emp_id'])

    # Fetch a location
    def get_location(self, store_id=None):
        path = f'/api/location/{store_id}'
        req = requests.get(self.url(path, pretty=True), headers=self._headers())

        location_data = json.loads(req.text)

        loc = location_data['data']['location']
        return self.Location(location_id=loc['id'],
                             wss_url=loc['wssUrl'],
                             default_order_notes=loc['defaultOrderNotes'],
                             name=loc['name'],
                             address=loc['address'],
                             phone=loc['phone'])

    # Fetch all items
    def get_items(self, store_id=None):
        items = []
        path = f'/api/location/{store_id}/items'

        req = requests.get(self.url(path, pretty=True), headers=self._headers())

        items_data = json.loads(req.text)

        for item in items_data['data']['items']:
            items.append(self.Item(item_id=item['id'],
                                   name=item['name'],
                                   description=item['description'],
                                   reporting_categories=item['reportingCategories'],
                                   tax_rates=item['taxRates'],
                                   item_type=item['type']))
        return items

    # Fetch an item
    def get_item(self, store_id=None, item_id=None):
        path = f'/api/location/{store_id}/items/{item_id}'
        req = requests.get(self.url(path, pretty=True), headers=self._headers())

        item_data = json.loads(req.text)

        item = item_data['data']['items'][0]

        return self.Item(item_id=item['id'],
                         name=item['name'],
                         description=item['description'],
                         reporting_categories=item['reportingCategories'],
                         tax_rates=item['taxRates'],
                         item_type=item['type'])