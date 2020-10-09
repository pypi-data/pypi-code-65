from rest_framework import serializers


class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    childs = serializers.SerializerMethodField()

    @classmethod
    def get_childs(cls, obj):
        return cls(obj.category_set.all(), many=True).data or None


class CategoryRecursiveSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    parent = serializers.SerializerMethodField()

    @classmethod
    def get_parent(cls, obj):
        if obj.parent:
            return cls(obj.parent).data
