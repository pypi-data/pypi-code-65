#      Copyright (C) 2020 <Florian Alu - Prolibre - https://prolibre.com
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU Affero General Public License as
#      published by the Free Software Foundation, either version 3 of the
#      License, or (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU Affero General Public License for more details.
#
#      You should have received a copy of the GNU Affero General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.

# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class Holiday(models.Model):
    name = models.CharField(_("Name"), max_length=50)
    date = models.DateField(_("Date"))

    class Meta:
        ordering = ['date']
        verbose_name = _("Holiday")
        verbose_name_plural = _("Holidays")

    def __str__(self):  # __unicode__ on Python 2
        # Returns the person's full name.
        return "{} - {}".format(self.name, self.date)


class Company(TimeStampedModel):
    """ models for Company """
    name = models.CharField(_("Name"), max_length=100, unique=True)
    short_code = models.SlugField(_("Short code"), unique=True)

    class Meta:
        ordering = ('name', 'short_code',)
        verbose_name = _('Company')
        verbose_name_plural = _('Companies')
        unique_together = ("name", "short_code")

    def __str__(self):
        return "{} - {}".format(self.name, self.short_code)


class CompanyClosure(TimeStampedModel):
    """ Models for Company closure """
    from_date = models.DateField(_("From date"))
    end_date = models.DateField(_("End date"))
    desc = models.CharField(_("Description"), max_length=100, blank=True, null=True)
    company = models.ForeignKey(
        verbose_name=_("Company"),
        to=Company,
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ('from_date', 'end_date')
        verbose_name = _('Company closure')
        verbose_name_plural = _('Company closures')

    def __str__(self):
        return "{} ({} | {})".format(self.company.name, self.from_date, self.end_date)
