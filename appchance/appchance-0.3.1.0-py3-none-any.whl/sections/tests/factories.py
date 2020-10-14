import factory
import swapper

Section = swapper.load_model("pychance_sections", "Section")
Content = swapper.load_model("pychance_sections", "Content")
SectionContent = swapper.load_model("pychance_sections", "SectionContent")


class SectionFactory(factory.django.DjangoModelFactory):
    location = factory.Iterator([choice[0] for choice in Section.POSITION_CHOICES])
    type = factory.Iterator([choice[0] for choice in Section.TYPE_CHOICES])
    name = factory.Faker("pystr")

    class Meta:
        model = Section


class ContentFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("pystr")
    redirect_url = factory.Faker("ipv4")
    content_url = factory.Faker("ipv4")

    class Meta:
        model = Content


class SectionContentFactory(factory.django.DjangoModelFactory):
    order = factory.Faker("pyint")
    section = factory.SubFactory(SectionFactory)
    content = factory.SubFactory(ContentFactory)

    class Meta:
        model = SectionContent
