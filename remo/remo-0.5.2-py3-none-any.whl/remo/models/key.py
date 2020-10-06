from django.db import models


class Key(models.Model):
    key = models.TextField(blank=True, null=True, default='')

    class Meta:
        db_table = 'keys'


