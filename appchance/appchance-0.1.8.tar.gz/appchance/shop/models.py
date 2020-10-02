from django.db import models


class PyProduct(models.Model):
    """ Product in shop.
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    sku = models.CharField(max_length=20, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

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

class PyHomeSection(models.Model):
    """ Homescreen section.
    """

    name = models.CharField(max_length=80)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True
