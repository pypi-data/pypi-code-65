import swapper
from django.db import models
from django.db.models import Prefetch


class BaseSectionQuerySet(models.QuerySet):
    def prefetch_content(self):
        SectionContent = swapper.load_model("pychance_sections", "SectionContent")

        return self.prefetch_related(
            Prefetch("content_list", queryset=SectionContent.objects.order_by("order").select_related("content"))
        )
