import os

from django.db import models


class PicturePost(models.Model):
    """Main picture post object.

    Takes the name, description, picture and optionally source of picture,
    then data is put in the index page of photogallery, from where can be 
    clicked to move into details.

    Attributes:
        picture: Field for image from admin.
        name: Name of the post.
        description: Description of the post.
        source: URL to source of image.
    """
    picture = models.ImageField(upload_to = '', height_field="url_height", width_field="url_width")
    name = models.CharField(max_length=30)
    description = models.TextField()
    pub_date = models.DateTimeField('Publication date', auto_now=True)
    objects = models.Manager()
    source = models.CharField(max_length=255, blank=True)
    url_height=models.PositiveIntegerField()
    url_width=models.PositiveIntegerField()

    def __str__(self):
        return self.name

    def filename(self):
        return os.path.basename(self.picture)
