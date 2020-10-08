from django.db import models


class PyProduct(models.Model):
    """ Product in shop.
    """
    sku = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    short_description = models.CharField(blank=True, max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"({self.sku}) {self.name}"

class PyCategory(models.Model):
    """ Category of products.
    """
    name = models.CharField(max_length=255)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class PyBrand(models.Model):
    """ Product's Brand.
    """

    name = models.CharField(max_length=80)

    class Meta:
        abstract = True


class PyHomeSection(models.Model):
    """ Homescreen section.
    """

    name = models.CharField(max_length=80)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True
