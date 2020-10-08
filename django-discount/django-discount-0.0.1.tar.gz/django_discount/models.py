import math
import datetime

from django.db import models
from django.contrib.auth import get_user_model
# from django.utils.translation import ugettext as _
# from django.contrib.postgres.fields import ArrayField

from .utils import price_beautifier
from .consts import *

User = get_user_model()


class DiscountManager(models.Manager):

    def check_code(self, code, item_type, item_id, user_id, amount=None):
        """ Will check code, and find proper discount for it, then will do some validations
        if this code is valid for this user and this item or not. Then will calculate
        total discount for amount of transaction."""

        # First check if this discount item do exist
        discount = self.filter(code=code).prefetch_related('items').first()
        if not discount:
            return False, 0, 'کد تخفیف نامعتبر است.'

        is_available, msg = discount.is_available(user_id)
        if not is_available:
            return False, 0, msg

        # Now verify if the item_type and item_id items do exist in list if DiscountItems
        status, msg = discount.check_if_item_allowed(item_type, item_id)
        if not status:
            return False, 0, msg

        discount_amount = 0
        if amount:
            # If amount not provided, means we are just checking if code is valid or not!
            if amount < discount.min_invoice_amount:
                return False, 0, 'حداقل میزان تراکنش برای اعمال این کد تخفیف {} تومان است.'.format(
                    price_beautifier(discount.min_invoice_amount)
                )

            discount_amount = discount.calc_discount(amount)
        return True, discount_amount, 'معتبر است.'


class Discount(models.Model):
    title = models.CharField(
        max_length=100,
        verbose_name='عنوان کد تخفیف'
    )
    code = models.CharField(
        max_length=20,
        verbose_name='کد تخفیف'
    )

    # Discount amount to apply
    type = models.CharField(
        choices=DISCOUNT_TYPES,
        verbose_name='نوع تخفیف',
        max_length=10,
        default='percent'
    )
    value = models.PositiveIntegerField(
        default=0,
        verbose_name='میزان تخفیف'
    )

    # Limitations
    min_invoice_amount = models.IntegerField(
        verbose_name='حداقل مبلغ فاکتور برای اعمال تخفیف',
        default=10000,
    )
    max_amount = models.IntegerField(
        default=100000,
        verbose_name='حداکثر میزان تخفیف',
        help_text='در صورتی که میزان تخفیف بیش از این عدد شود،'
                  ' تنها این میزان اعمال خواهد شد.'
    )

    # Usage Parameters
    total_max_uses = models.IntegerField(
        default=50,
        verbose_name='حداکثر تعداد دفعاتی که این کد تخفیف قابل استفاده است.'
    )
    total_uses = models.IntegerField(
        default=0,
        verbose_name='تعداد دفعات استفاده شده'
    )

    # Date attributes
    start_date = models.DateTimeField(
        null=True, blank=True,
        verbose_name='زمان شروع تخفیف',
        help_text='در صورت خالی بودن زمان شروع حال در نظر گرفته می‌شود.'
    )
    expire_date = models.DateTimeField(
        null=True, blank=True, verbose_name='زمان پایان اعتبار کد تخفیف',
        help_text='در صورتی که خالی تعریف شد، کد تخفیف منقضی نخواهد شد.'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='وضعیت فعال بودن کد تخفیف'
    )
    not_active_reason = models.CharField(
        max_length=100, default='',
        verbose_name='علت غیرفعال بودن', blank=True
    )
    is_deleted = models.BooleanField(
        default=False,
        verbose_name="حذف شد"
    )

    objects = DiscountManager()

    def __str__(self):
        return '{}, {}'.format(self.title, self.code)

    class Meta:
        db_table = 'discount'
        verbose_name = 'کد تخفیف'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.start_date:
            self.start_date = datetime.datetime.now()
        if not self.expire_date:
            self.expire_date = self.start_date + datetime.timedelta(days=30)
        if self.expire_date <= self.start_date:
            raise ValueError('زمان انقضای کد تخفیف نمی‌تواند بیش‌تر از زمان شروع آن باشد.')

        if not self.pk:
            if Discount.objects.filter(code=self.code).exists():
                raise ValueError('این کد قبلا تعریف شده است.')

        # In percent type, value should be between 0 and 100
        if self.type == 'percent':
            if not 0 <= self.value <= 100:
                raise ValueError('مقدار باید بین ۰ تا ۱۰۰ باشد.')

        super(Discount, self).save()

    def is_available(self, user_id=None):
        if not self.is_active:
            msg = 'کد تخفیف فعال نیست.'
            return False, msg
        if self.total_uses >= self.total_max_uses:
            msg = 'کد تخفیف منقضی شده است.'
            self.deactivate(msg, True)
            return False,
        now = datetime.datetime.now()
        if now < self.start_date:
            msg = 'مهلت استفاده از کد تخفیف هنوز شروع نشده است.'
            return False, msg
        if now > self.expire_date:
            msg = 'کد تخفیف منقضی شده است.'
            self.deactivate(msg, True)
            return False, msg

        # Now check if user is already used this discount code or not!
        # if count bigger than max usage it ignore system
        if user_id:
            count_discount = UsedDiscount.objects.filter(user_id=user_id, discount_id=self.id).count()
            if count_discount >= self.total_max_uses:
                msg = 'شما از این کد تخفیف {} استفاده کرده‌اید واین حدکثر تعداد مجاز برای شماست.'.format(count_discount)
                return False, msg
            # if UsedDiscount.objects.filter(user_id=user_id, discount=self):
            #     msg = 'شما قبلا از این کد تخفیف استفاده کرده‌اید.'
            #     return False, msg
        return True, ''

    def deactivate(self, msg='', commit=True):
        self.is_active = False
        if msg:
            self.not_active_reason = msg
        if commit:
            self.save()

    def calc_discount(self, amount):
        """ Will calculate how much value of discount will be if is applied on amount. """
        if self.type == 'percent':
            discount = math.ceil(amount * self.value / 100)
        else:
            discount = self.value
        if discount > self.max_amount:
            discount = self.max_amount
        return discount

    def check_if_item_allowed(self, item_type, item_id):
        item = self.items.filter(type=item_type).first()
        if not item:
            return False, 'کد تخفیف برای این آیتم تعریف نشده است.'
        if not item.id_list or item_id in item.id_list:
            return True, ''
        return False, 'کد تخفیف برای این آیتم تعریف نشده است.'


# class DiscountItem(models.Model):
#     """ Model will hold items and their list of item IDs.
#     So whenever we want to validate a discount code on an item,
#     Will check it's type and id with this model. """
#     discount = models.ForeignKey(
#         Discount,
#         on_delete=models.CASCADE,
#         related_name='items'
#     )
#     type = models.CharField(
#         choices=DISCOUNT_ITEM_TYPES,
#         default='hotel', max_length=10,
#         verbose_name='نوع آیتمی که کد می‌تواند بر روی آن اعمال شود.'
#     )
#     id_list = ArrayField(
#         models.IntegerField(null=True, blank=True), default=list, blank=True,
#         verbose_name='لیست آی‌دی‌های این نوع آیتم که بر روی آن‌ها قابل اعمال است.',
#         help_text='در صورتی که خالی باشد بر روی تمامی آیتم‌های این نوع قابل استفاده است.'
#     )
#
#     def __str__(self):
#         return '{} {}'.format(
#             self.get_type_display(),
#             self.discount.__str__()
#         )
#
#     class Meta:
#         db_table = 'discount_item'
#         verbose_name_plural = 'آیتم‌های کد تخفیف'
#
#     def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
#         """
#         if discount not exist will be added but if discount and type exist will be update this discount id
#         :param force_insert:
#         :param force_update:
#         :param using:
#         :param update_fields:
#         :return:
#         """
#         if not self.pk:
#             dis_val = DiscountItem.objects.filter(
#                 discount=self.discount,
#                 type=self.type
#             )
#             if len(dis_val) > 0:
#                 DiscountItem.objects.filter(id=dis_val[0].id).update(id_list=self.id_list)
#                 return "update:{}".format(dis_val[0])
#             # raise ValueError('این نوع آیتم قبلا تعریف شده است.')
#             # super(DiscountItem,self).update()
#             else:
#                 super(DiscountItem, self).save()
#         # super(DiscountItem, self).save()
#
#
# class UsedDiscount(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discounts')
#     discount = models.ForeignKey(Discount, on_delete=models.CASCADE)
#     item_type = models.CharField(choices=DISCOUNT_ITEM_TYPES, default='hotel', max_length=10)
#     item_id = models.IntegerField(null=True, blank=True)
#
#     def __str__(self):
#         return "{},{}".format(self.discount.title, self.item_id)
