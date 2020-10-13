from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django_countries import Countries
from django_countries.fields import CountryField
import datetime

class CaribbeanCountries(Countries):
    only = [
        ('AI',_('Anguilla')),
        ('AG',_('Antigua and Barbuda')),
        ('AW',_('Aruba')),
        ('BS',_('Bahamas')),
        ('BB',_('Barbados')),
        ('BZ',_('Belize')),
        ('BM',_('Bermuda')),
        ('BQ',_('Bonaire, Sint Eustatius and Saba')),
        ('VG',_('British Virgin Islands')),
        ('KY',_('Cayman Islands')),
        ('CU',_('Cuba')),
        ('CW',_('Curacao')),
        ('DM',_('Dominica')),
        ('DO',_('Dominican Republic')),
        ('GF',_('French Guiana')),
        ('GD',_('Grenada')),
        ('GP',_('Guadeloupe')),
        ('GY',_('Guyana')),
        ('HT',_('Haiti')),
        ('JM',_('Jamaica')),
        ('MQ',_('Martinique')),
        ('MS',_('Montserrat')),
        ('PR',_('Puerto Rico')),
        ('BL',_('Saint Barthelemy')),
        ('KN',_('Saint Kitts and Nevis')),
        ('LC',_('Saint Lucia')),
        ('MF',_('Saint Martin')),
        ('VC',_('Saint Vincent and the Grenadines')),
        ('SX',_('Sint Maarten')),
        ('SR',_('Suriname')),
        ('TT',_('Trinidad and Tobago')),
        ('TC',_('Turks and Caicos Islands')),
        ('VI',_('United States Virgin Islands')),
    ]


class ParentCountries(Countries):
    only = ['FR', 'NL', 'US', 'GB']


class Demographics(models.Model):
    country = CountryField(countries=CaribbeanCountries, unique=True)
    parent_country = CountryField(countries=ParentCountries, null=True, blank=True)
    year_of_data = models.PositiveIntegerField(null=False, blank=False)
    country_area = models.PositiveIntegerField(null=False, blank=False)
    latitude = models.DecimalField(null=False, blank=False, default=0, max_digits=9, decimal_places=6)
    longitude = models.DecimalField(null=False, blank=False, default=0, max_digits=9, decimal_places=6)
    country_population = models.PositiveIntegerField(null=False, blank=False)
    caricom = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        verbose_name_plural = _('Demographics')

    def __str__(self):
        return '%s (%s)' % (self.country.name,self.country)


class Disease(models.Model):
    name = models.CharField(max_length=30, null=False, blank=False)
    description = models.TextField(max_length=1000,null=False, blank=False)
    code_name = models.CharField(max_length=30,null=False, blank=False)
    reference_url = models.URLField(null=True, blank=True)
    start_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name_plural = _('Diseases')

    def __str__(self):
        return '%s (%s)' % (self.name, self.code_name)


class TrackerLog(models.Model):
    disease = models.ForeignKey(Disease, related_name='disease_tracker_logs', on_delete=models.CASCADE)
    country = models.ForeignKey(Demographics, related_name='country_tracker_logs', on_delete=models.CASCADE)
    date = models.DateField(null=False)
    total_cases = models.PositiveIntegerField(default=0)
    total_new_cases = models.IntegerField(default=0, editable=False)
    total_deaths = models.PositiveIntegerField(default=0)
    total_new_deaths = models.IntegerField(default=0, editable=False)
    recovered = models.PositiveIntegerField(default=0)
    incidence_rate = models.DecimalField(default=0, max_digits=7, decimal_places=2, editable=False)
    case_fatality_ratio = models.DecimalField(default=0, max_digits=7, decimal_places=2, editable=False)
    source_name = models.CharField(max_length=30, null=False)
    source_url = models.URLField()
    is_published = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    
    class Meta:
        verbose_name_plural = _('Tracker Logs')

    def __str__(self):
        return '%s Log #%s for %s [%s]' % (self.disease.code_name, str(self.pk), self.country.country.name, self.date)


class FAQSection(models.Model):
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE)
    title = models.CharField(max_length=60, null=False, blank=False)
    priority = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name_plural = _('FAQ Sections')

    def __str__(self):
        return 'Section #%s - %s [%s]' % (str(self.pk), self.title, self.disease.code_name)


class FAQDetail(models.Model):
    section = models.ForeignKey(FAQSection, on_delete=models.CASCADE)
    question = models.CharField(max_length=120, null=False, blank=False)
    answer = models.TextField(null=False, blank=False)
    priority = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name_plural = _('FAQ Details')

    def __str__(self):
        return '#%s - %s' % (str(self.pk), self.question)


@receiver(pre_save, sender=TrackerLog)
def auto_calculate(sender, instance, *args, **kwargs):
    try:
        previous_date = instance.date - datetime.timedelta(days=1)
        previous_rec = TrackerLog.objects.get(date=previous_date,disease__pk=instance.disease.pk,country__pk=instance.country.pk)
        instance.total_new_cases = instance.total_cases - previous_rec.total_cases
        instance.total_new_deaths = instance.total_deaths - previous_rec.total_deaths
    except TrackerLog.DoesNotExist:
        instance.total_new_cases = 0
        instance.total_new_deaths = 0
    except:
        pass

    population = Demographics.objects.get(pk=instance.country.pk).country_population
    try:
        instance.incidence_rate = (float(instance.total_cases) / float(population)) * 100000
    except ZeroDivisionError:
        instance.incidence_rate = 0
    except:
        pass

    try:
        instance.case_fatality_ratio = (instance.total_deaths / instance.total_cases) * 100
    except ZeroDivisionError:
        instance.case_fatality_ratio = 0
    except:
        pass    
