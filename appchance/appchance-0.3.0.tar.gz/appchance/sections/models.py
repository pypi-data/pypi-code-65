import swapper
from django.db import models
from django.utils.translation import gettext_lazy as _

from appchance.sections.querysets import BaseSectionQuerySet


class BaseSection(models.Model):
    POSITION_TOP = 1
    POSITION_CHOICES = [
        (POSITION_TOP, _("top")),
    ]

    TYPE_BANNER = 1
    TYPE_SLIDER = 2

    TYPE_CHOICES = [
        (TYPE_BANNER, _("banner")),
        (TYPE_SLIDER, _("slider")),
    ]

    name = models.CharField(blank=True, max_length=255)
    location = models.PositiveSmallIntegerField(_("location"), choices=POSITION_CHOICES, blank=True, null=True)
    type = models.PositiveSmallIntegerField(_("type"), choices=TYPE_CHOICES, blank=True, null=True)

    objects = BaseSectionQuerySet.as_manager()

    @property
    def content(self):
        return self.content_list.order_by("order").select_related("content").all()

    class Meta:
        abstract = True


class Section(BaseSection):
    class Meta:
        swappable = swapper.swappable_setting("pychance_sections", "Section")


class BaseContent(models.Model):
    name = models.CharField(_("name"), blank=True, max_length=255)
    redirect_url = models.URLField(_("redirect url"), blank=True, null=True)
    content_url = models.URLField(_("content url"), blank=True, null=True)

    class Meta:
        abstract = True


class Content(BaseContent):
    class Meta:
        swappable = swapper.swappable_setting("pychance_sections", "Content")


class BaseSectionContent(models.Model):
    section = models.ForeignKey(
        swapper.get_model_name("pychance_sections", "Section"), on_delete=models.CASCADE, related_name="content_list"
    )
    content = models.ForeignKey(
        swapper.get_model_name("pychance_sections", "Content"), on_delete=models.CASCADE, related_name="content_list"
    )
    order = models.PositiveSmallIntegerField(_("order"), default=0)

    class Meta:
        abstract = True
        ordering = ("order",)


class SectionContent(BaseSectionContent):
    class Meta:
        swappable = swapper.swappable_setting("pychance_sections", "SectionContent")
