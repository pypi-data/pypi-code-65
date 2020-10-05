import graphene
from graphene_django import DjangoObjectType
from .models import Premium
from core import prefix_filterset, filter_validity, ExtendedConnection
from policy.schema import PolicyGQLType
from payer.schema import PayerGQLType

class PremiumGQLType(DjangoObjectType):
    class Meta:
        model = Premium
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "uuid": ["exact"],
            "amount": ["exact", "lt", "lte", "gt", "gte"],
            **prefix_filterset("payer__", PayerGQLType._meta.filter_fields),
            **prefix_filterset("policy__", PolicyGQLType._meta.filter_fields)
        }
        connection_class = ExtendedConnection
