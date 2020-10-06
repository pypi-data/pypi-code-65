from django.db import models
from django.contrib.auth import get_user_model


class Log(models.Model):
    class Category(models.TextChoices):
        RESERVE = 'reserve'

    user = models.ForeignKey(
        to=get_user_model(),
        on_delete=models.CASCADE,
        related_name='logs',
        related_query_name='log'
    )
    category = models.CharField(max_length=1000, choices=Category.choices)
    description = models.TextField()
    reference_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True)

    def __str__(self):
        return F"{self.category}"

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'log'
        verbose_name_plural = 'log'
