from pymasmovil.models.contract import Contract


class Asset(Contract):
    _route = '/v1/assets'

    maxNumTariff = ''
    numTariff = ''
    productRelation = ''
    assetType = ''
    initDate = ''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def get(cls, session, asset_id):
        contract = super().get(session, asset_id)

        return cls(**contract['asset'])
