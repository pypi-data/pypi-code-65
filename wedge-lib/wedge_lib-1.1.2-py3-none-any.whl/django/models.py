from django.db import models


class AbstractCreatedUpdatedModel(models.Model):
    created_at = models.DateTimeField("crée le", auto_now_add=True)
    updated_at = models.DateTimeField("maj le", auto_now=True)

    class Meta:
        abstract = True


class Reference(AbstractCreatedUpdatedModel):
    code = models.CharField(max_length=20, primary_key=True)
    label = models.CharField(max_length=100)

    class Meta:
        abstract = True
        ordering = ["label"]

    def __str__(self):
        return self.label
