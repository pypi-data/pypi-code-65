import pytest
import swapper

from appchance.sections.tests.factories import SectionContentFactory

Section = swapper.load_model("pychance_sections", "Section")
SectionContent = swapper.load_model("pychance_sections", "SectionContent")


@pytest.mark.django_db
class TestSectionQuerySet:
    def test_prefetch_content__content_prefetched(self):
        SectionContentFactory()
        sections = Section.objects.prefetch_content().all()
        assert len(sections[0]._prefetched_objects_cache) > 0
