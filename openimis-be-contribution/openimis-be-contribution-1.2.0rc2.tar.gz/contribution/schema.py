from django.db.models import Q
from django.core.exceptions import PermissionDenied
from graphene_django.filter import DjangoFilterConnectionField
import graphene_django_optimizer as gql_optimizer

from .apps import ContributionConfig
from django.utils.translation import gettext as _
from core.schema import OrderedDjangoFilterConnectionField
from policy import models as policy_models
from .models import Premium
# We do need all queries and mutations in the namespace here.
from .gql_queries import *  # lgtm [py/polluting-import]
from .gql_mutations import *  # lgtm [py/polluting-import]

class Query(graphene.ObjectType):
    premiums = OrderedDjangoFilterConnectionField(
        PremiumGQLType,
        orderBy=graphene.List(of_type=graphene.String),
    )
    premiums_by_policies = OrderedDjangoFilterConnectionField(
        PremiumGQLType,
        policy_uuids=graphene.List(graphene.String, required=True),
        orderBy=graphene.List(of_type=graphene.String),
    )

    def resolve_premiums(self, info, **kwargs):
        if not info.context.user.has_perms(ContributionConfig.gql_query_premiums_perms):
            raise PermissionDenied(_("unauthorized"))
        pass

    def resolve_premiums_by_policies(self, info, **kwargs):
        if not info.context.user.has_perms(ContributionConfig.gql_query_premiums_perms):
            raise PermissionDenied(_("unauthorized"))
        policies = policy_models.Policy.objects.values_list('id').filter(Q(uuid__in=kwargs.get('policy_uuids')))
        return Premium.objects.filter(Q(policy_id__in=policies), *filter_validity(**kwargs))
