from django.contrib.auth import get_user_model
from rest_framework import serializers
# from rest_framework.serializers import Serializer
from bitmex_journal_backend.reversable_primary_key.primary_key import reverse_id


class CreatedSerializerMixin(serializers.Serializer):

    created = serializers.SerializerMethodField()
    def get_created(self, obj):
        try:
            return reverse_id(obj.id)
        except Exception:
            return None