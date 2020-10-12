from djangoldp.permissions import LDPPermissions
from django.db.models.base import ModelBase
from django.conf import settings


class CommunityPermissions(LDPPermissions):
    def user_permissions(self, user, obj_or_model, obj=None):
        if not isinstance(obj_or_model, ModelBase):
            obj = obj_or_model

        perms = set(super().user_permissions(user, obj_or_model, obj))

        # Communities affiliations list are public
        perms = perms.union({'view'})

        if obj:
            community = obj
            membership = None

            if hasattr(obj, 'community'):
                community = obj.community

            if not user.is_anonymous:
                try:
                    membership = community.members.get(user=user)
                except:
                    membership = None

            if membership:
                perms = perms.union({'view', 'add'})

                if getattr(membership, 'is_admin', False):
                    perms = perms.union({'change', 'delete'})

        return list(perms)
