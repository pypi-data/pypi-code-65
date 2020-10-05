import uuid

from core import fields
from core import models as core_models
from django.db import models


class PayerType(models.Model):
    code = models.CharField(db_column='Code', primary_key=True, max_length=1)
    payer_type = models.CharField(db_column='PayerType', max_length=50)
    alt_language = models.CharField(db_column='AltLanguage', max_length=50, blank=True, null=True)
    sort_order = models.IntegerField(db_column='SortOrder', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblPayerType'


class Payer(core_models.VersionedModel):
    id = models.AutoField(db_column='PayerID', primary_key=True)
    uuid = models.CharField(db_column='PayerUUID', max_length=36, default=uuid.uuid4, unique=True)

    type = models.ForeignKey(
        PayerType, models.DO_NOTHING, db_column='PayerType', blank=True, null=True)
    name = models.CharField(db_column='PayerName', max_length=100, null=False)
    address = models.CharField(db_column='PayerAddress', max_length=100, null=True, blank=True)
    location = models.ForeignKey("location.Location", db_column="LocationId", blank=True, null=True,
                                 on_delete=models.DO_NOTHING, related_name='+')
    phone = models.CharField(db_column='Phone', max_length=50, null=True, blank=True)
    fax = models.CharField(db_column='Fax', max_length=50, null=True, blank=True)
    email = models.CharField(db_column='eMail', max_length=50, null=True, blank=True)

    audit_user_id = models.IntegerField(db_column='AuditUserID')
    # rowid = models.TextField(db_column='RowID', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblPayer'
