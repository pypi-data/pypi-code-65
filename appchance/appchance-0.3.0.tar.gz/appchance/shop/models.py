from django.db import models


class PyShop(models.Model):
    """Shop."""

    name = models.CharField(max_length=120)
    code = models.CharField(max_length=50)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class PyBrand(models.Model):
    """Product's brand."""

    name = models.CharField(max_length=80)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class PyCategory(models.Model):
    """Category of products."""

    name = models.CharField(max_length=255)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class PyProduct(models.Model):
    """Product in shop."""

    # General
    sku = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    short_description = models.CharField(blank=True, max_length=255)
    description = models.TextField(blank=True)

    # Flags
    is_cc = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def __str__(self):
        return f"({self.sku}) {self.name}"


class PyProductSize(models.Model):
    """Product size: width, height, depth and weight."""

    size_width = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    size_height = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    size_depth = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    size_weight = models.DecimalField(max_digits=20, decimal_places=6, default=0)

    class Meta:
        abstract = True


class PyHomeSection(models.Model):
    """Homescreen section."""

    name = models.CharField(max_length=80)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True
