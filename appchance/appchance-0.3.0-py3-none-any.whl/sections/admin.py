import swapper
from django.contrib import admin

Section = swapper.load_model("pychance_sections", "Section")
SectionContent = swapper.load_model("pychance_sections", "SectionContent")
Content = swapper.load_model("pychance_sections", "Content")


class ContentListInline(admin.StackedInline):
    model = SectionContent
    extra = 1


@admin.register(Content)
class SectionContentAdmin(admin.ModelAdmin):
    inlines = (ContentListInline,)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    inlines = (ContentListInline,)
