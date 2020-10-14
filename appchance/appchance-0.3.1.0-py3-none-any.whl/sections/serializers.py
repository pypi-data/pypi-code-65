import swapper
from rest_framework import serializers

Section = swapper.load_model("pychance_sections", "Section")
Content = swapper.load_model("pychance_sections", "Content")
SectionContent = swapper.load_model("pychance_sections", "SectionContent")


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = "__all__"


class SectionContentSerializer(serializers.ModelSerializer):
    content = ContentSerializer()

    class Meta:
        model = SectionContent
        fields = "__all__"


class SectionSerializer(serializers.ModelSerializer):
    content_list = SectionContentSerializer(many=True)

    class Meta:
        model = Section
        fields = "__all__"
