from django.contrib import admin

from .models import PicturePost
# Register your models here.
class PicturePostAdmin(admin.ModelAdmin):
    """Limites data input on posting site.

    Divides the input data to necessary and unnecessary.

    Atributes:
        fieldsets = Divides post site into sections
    """
    fieldsets = [("Post", {'fields':['name', 'description', 'picture']}),
         ("Post info", {'fields':['source']})]

admin.site.register(PicturePost, PicturePostAdmin)
