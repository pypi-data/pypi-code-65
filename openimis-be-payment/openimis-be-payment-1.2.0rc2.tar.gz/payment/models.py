import uuid

from core import fields
from core import models as core_models
from django.db import models
from contribution.models import Premium


class Payment(core_models.VersionedModel):
    id = models.BigAutoField(db_column='PaymentID', primary_key=True)
    uuid = models.CharField(db_column='PaymentUUID', max_length=36)

    expected_amount = models.DecimalField(db_column='ExpectedAmount', max_digits=18, decimal_places=2, blank=True, null=True)
    received_amount = models.DecimalField(db_column='ReceivedAmount', max_digits=18, decimal_places=2, blank=True, null=True)
    officer_code = models.CharField(db_column='OfficerCode', max_length=50, blank=True, null=True)
    phone_number = models.CharField(db_column='PhoneNumber', max_length=12, blank=True, null=True)
    request_date = fields.DateField(db_column='RequestDate', blank=True, null=True)
    received_date = fields.DateField(db_column='ReceivedDate', blank=True, null=True)
    status = models.IntegerField(db_column='PaymentStatus', blank=True, null=True)

    transaction_no = models.CharField(db_column='TransactionNo', max_length=50, blank=True, null=True)
    origin = models.CharField(db_column='PaymentOrigin', max_length=50, blank=True, null=True)
    matched_date = fields.DateField(db_column='MatchedDate', blank=True, null=True)
    receipt_no = models.CharField(db_column='ReceiptNo', max_length=100, blank=True, null=True)
    payment_date = fields.DateField(db_column='PaymentDate', blank=True, null=True)
    rejected_reason = models.CharField(db_column='RejectedReason', max_length=255, blank=True, null=True)
    date_last_sms = fields.DateField(db_column='DateLastSMS', blank=True, null=True)
    language_name = models.CharField(db_column='LanguageName', max_length=10, blank=True, null=True)
    type_of_payment = models.CharField(db_column='TypeOfPayment', max_length=50, blank=True, null=True)
    transfer_fee = models.DecimalField(db_column='TransferFee', max_digits=18, decimal_places=2, blank=True, null=True)

    # rowid = models.TextField(db_column='RowID')
    # auditED, not audit ???
    # auditeduser_id = models.IntegerField(db_column='AuditedUSerID', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblPayment'


class PaymentDetail(core_models.VersionedModel):
    id = models.BigAutoField(db_column='PaymentDetailsID', primary_key=True)

    payment = models.ForeignKey(Payment, models.DO_NOTHING, db_column='PaymentID', related_name="payment_details")
    # beware putting FKs: product code (,...): need to check if we can/must adapt payment info if code (,...) change
    # i.e. normally, FK is pointing to PK, not to a field
    product_code = models.CharField(db_column='ProductCode', max_length=8, blank=True, null=True)
    insurance_number = models.CharField(db_column='InsuranceNumber', max_length=12, blank=True, null=True)

    policy_stage = models.CharField(db_column='PolicyStage', max_length=1, blank=True, null=True)
    amount = models.DecimalField(db_column='Amount', max_digits=18, decimal_places=2, blank=True, null=True)

    premium = models.ForeignKey(Premium, models.DO_NOTHING, db_column='PremiumID', blank=True, null=True)

    enrollment_date = fields.DateField(db_column='enrollmentDate', blank=True, null=True)
    expected_amount = models.DecimalField(db_column='ExpectedAmount', max_digits=18, decimal_places=2, blank=True, null=True)

    # rowid = models.TextField(db_column='RowID', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    # auditED, not audit ???
    # auditeduserid = models.IntegerField(db_column='AuditedUserId', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblPaymentDetails'
