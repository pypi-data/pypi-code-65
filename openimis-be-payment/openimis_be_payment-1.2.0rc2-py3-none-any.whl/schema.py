from django.db.models import Q
from django.core.exceptions import PermissionDenied
from graphene_django.filter import DjangoFilterConnectionField
import graphene_django_optimizer as gql_optimizer

from .apps import PaymentConfig
from django.utils.translation import gettext as _
from core.schema import OrderedDjangoFilterConnectionField
from contribution import models as contribution_models
from .models import Payment, PaymentDetail
# We do need all queries and mutations in the namespace here.
from .gql_queries import *  # lgtm [py/polluting-import]
from .gql_mutations import *  # lgtm [py/polluting-import]


class Query(graphene.ObjectType):
    payments = OrderedDjangoFilterConnectionField(
        PaymentGQLType,
        orderBy=graphene.List(of_type=graphene.String),
    )
    payment_details = OrderedDjangoFilterConnectionField(
        PaymentDetailGQLType,
        orderBy=graphene.List(of_type=graphene.String),
    )
    payments_by_premiums = OrderedDjangoFilterConnectionField(
        PaymentGQLType,
        premium_uuids=graphene.List(graphene.String, required=True),
        orderBy=graphene.List(of_type=graphene.String),
    )

    def resolve_payments(self, info, **kwargs):
        if not info.context.user.has_perms(PaymentConfig.gql_query_payments_perms):
            raise PermissionDenied(_("unauthorized"))
        pass

    def resolve_payment_details(self, info, **kwargs):
        if not info.context.user.has_perms(PaymentConfig.gql_query_payments_perms):
            raise PermissionDenied(_("unauthorized"))
        pass

    def resolve_payments_by_premiums(self, info, **kwargs):
        if not info.context.user.has_perms(PaymentConfig.gql_query_payments_perms):
            raise PermissionDenied(_("unauthorized"))
        premiums = contribution_models.Premium.objects.values_list('id').filter(Q(uuid__in=kwargs.get('premium_uuids')))
        detail_ids = PaymentDetail.objects.values_list('payment_id').filter(Q(premium_id__in=premiums),
                                                                            *filter_validity(**kwargs)).distinct()
        return Payment.objects.filter(Q(id__in=detail_ids))
