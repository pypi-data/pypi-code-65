# touchpoint/location.py

'''This module defines a location.'''

class Location():
    '''
        The Location object contains a location's details
        :param location_id: Used to identify a given location
        :type location_id: str

        :param wss_url: Used to define a location's wss url
        :type wss_url: str

        :param default_order_notes: Used to define a location's default order notes
        :type default_order_notes: list

        :param name: Used to define a location's name
        :type name: str

        :param address:  Used to define a location's address
        :type address: str

        :param phone: Used to define a location's phone
        :type phone: str
    '''

    def __init__(self, location_id, wss_url=None, default_order_notes=None,
                 name=None, address=None, phone=None):

        if default_order_notes is None:
            self.default_order_notes = []
        else:
            self.default_order_notes = default_order_notes

        self.location_id = location_id
        self.wss_url = wss_url
        self.name = name
        self.address = address
        self.phone = phone

    def info(self):
        '''
            Returns a location's info.

            :returns: A location's info
            :rtype: dict
        '''

        return {'location_id': self.location_id,
                'wss_url': self.wss_url,
                'default_order_notes': self.default_order_notes,
                'name': self.name,
                'address': self.address,
                'phone': self.phone}
