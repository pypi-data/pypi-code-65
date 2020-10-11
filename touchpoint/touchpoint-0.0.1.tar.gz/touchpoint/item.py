# touchpoint/item.py

class Item():
    def __init__(self, item_id, name=None, description=None, item_type=None,
                 reporting_categories=None, tax_rates=None):

        if reporting_categories is None:
            self.reporting_categories = []
        else:
            self.reporting_categories = reporting_categories

        if tax_rates is None:
            self.tax_rates = []
        else:
            self.tax_rates = tax_rates

        self.item_id = item_id
        self.name = name
        self.description = description
        self.item_type = item_type

    def info(self):
        return {'item_id': self.item_id,
                'name': self.name,
                'description': self.description,
                'item_type': self.item_type,
                'reporting_categories': self.reporting_categories,
                'tax_rates': self.tax_rates}
