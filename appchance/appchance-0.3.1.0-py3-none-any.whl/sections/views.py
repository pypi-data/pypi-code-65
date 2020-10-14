import swapper
from rest_framework import viewsets
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import AllowAny

from appchance.sections.serializers import SectionSerializer

Section = swapper.load_model("pychance_sections", "Section")


class SectionViewSet(viewsets.GenericViewSet, ListModelMixin):
    permission_classes = (AllowAny,)
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
