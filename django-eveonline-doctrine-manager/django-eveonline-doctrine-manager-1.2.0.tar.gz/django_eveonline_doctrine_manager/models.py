from django.db import models
from django.apps import apps
from django_eveonline_connector.models import EveStructure, EveEntity, EveCharacter
from django_eveonline_connector.utilities.static.universe import resolve_type_name_to_type_id, get_type_id_prerq_skill_ids, get_prerequisite_skills, resolve_type_id_to_type_name, resolve_type_id_to_category_name
from django_eveonline_doctrine_manager.utilities.abstractions import EveSkillList
from django.core.validators import MaxValueValidator, MinValueValidator
from django_singleton_admin.models import DjangoSingleton
import json, logging, re, roman

logger = logging.getLogger(__name__)

"""
Helper functions
"""

bootstrap_color_choices = (
    ('primary', 'Blue'),
    ('secondary', 'Gray'),
    ('success', 'Green'),
    ('danger', 'Red'),
    ('warning', 'Yellow'),
    ('info', 'Light Blue'),
    ('dark', 'Dark Gray'),
)


def get_skill_names_from_static_dump():
    import django_eveonline_doctrine_manager
    import os
    pth = os.path.dirname(django_eveonline_doctrine_manager.__file__)
    with open(pth + '/export/skills.json', 'r') as fp:
        skills = json.load(fp)

    return [ (skill, skill) for skill in skills.keys()]

class EveDoctrineSettings(DjangoSingleton):
    staging_structure = models.OneToOneField(EveStructure, on_delete=models.SET_NULL, null=True, blank=True)
    contract_entity = models.OneToOneField(EveEntity, on_delete=models.SET_NULL, null=True, blank=True)
    seeding_enabled = models.BooleanField(default=False)

    @staticmethod
    def get_instance():
        return EveDoctrineSettings.objects.all()[0]

    class Meta:
        verbose_name = "Eve Doctrine Settings"
        verbose_name_plural = "Eve Doctrine Settings"

"""
Core models
These are the main data models for the doctrine manager
"""


class EveDoctrine(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField("EveDoctrineManagerTag", blank=True)
    category = models.ForeignKey(
        "EveDoctrineCategory", on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def fittings(self):
        return EveFitting.objects.filter(doctrines__in=[self])
    
    @property
    def skill_plans(self):
        return EveSkillPlan.objects.filter(doctrines__in=[self])

    @property
    def character_list(self):
        return EveCharacter.objects.filter(corporation__track_characters=True)

    def __str__(self):
        return self.name

    
class EveFitting(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField("EveDoctrineManagerTag", blank=True)
    doctrines = models.ManyToManyField("EveDoctrine", blank=True)
    roles = models.ManyToManyField("EveDoctrineRole", blank=True)
    fitting = models.TextField()  # eft format
    # eve static info
    ship_id = models.IntegerField(editable=False, blank=True, null=True)
    # associations 
    refit_of = models.ForeignKey("EveFitting", blank=True, null=True, default=None, on_delete=models.CASCADE)

    @property
    def refits(self):
        return EveFitting.objects.filter(refit_of=self)

    def save(self, *args, **kwargs):
        self.ship_id = resolve_type_name_to_type_id(self.get_ship_name())
        super(EveFitting, self).save(*args, **kwargs)
    
    @property
    def character_list(self):
        return EveCharacter.objects.filter(corporation__track_characters=True)

    def __str__(self):
        return self.name

    def get_ship_name(self):
         fitting = self.fitting.splitlines()
         line = fitting[0]
         return line[1:-1].split(',')[0].strip()

    def get_required_skills(self):
        fitting = self.parse_fitting()
        exclude_keys = ['ship']
        top_level_skills = []

        for key in fitting:
            
            if key in exclude_keys:
                continue

            module_list = fitting[str(key)]
            unique_modules = set()
            unique_modules.add(fitting['ship']['type_id'])
            for module in module_list:
                unique_modules.add(module['type_id'])

            for module in unique_modules:
                top_level_skills += get_type_id_prerq_skill_ids(module)
            
            skill_list = EveSkillList()
            for skill in top_level_skills:
                for prerq_skill in reversed(get_prerequisite_skills([skill])):
                    skill_list.add_skill(prerq_skill)

        return skill_list  

    def parse_fitting(self):
        fit = {
            'ship': None,
            'highslots': [],
            'midslots': [],
            'lowslots': [],
            'rigs': [],
            'drones': [],
            'implants': [],
            'cargo': [],
        }

        regex_pattern = "(?P<type_name>[[A-Za-z0-9\-_' ]*(?<![x0-9]))(?P<loaded>,.*)?(?P<quantity>x[0-9]*)?"

        fitting = self.fitting.splitlines()
        fitting.reverse()
        ship_info_line = fitting.pop()
        ship_info = {
            'name': ship_info_line[1:-1].split(',')[1].strip(),
            'type_name': ship_info_line[1:-1].split(',')[0].strip(),
            'type_id': resolve_type_name_to_type_id(ship_info_line[1:-1].split(',')[0].strip()),
        }

        fit['ship'] = ship_info 
        case = -1
        cases = ['lowslots', 'midslots', 'highslots', 'rigs', 'items']
        while len(fitting) > 1:
            if (fitting[-1] == '' or fitting[-1].isspace()):
                line = fitting.pop()
                if case < 4:
                    case += 1
                while(fitting[-1].isspace() or fitting[-1] == ""):
                    excess = fitting.pop()
                continue
            else:
                line = fitting.pop()

            if 'Empty' in line or not line:
                continue
            
            results = re.search(regex_pattern, line)
            try:
                type_name = results.group('type_name').rstrip()
                quantity = results.group('quantity')
            except IndexError as e:
                pass # just means no quantity 
            type_id = resolve_type_name_to_type_id(type_name)
            category = resolve_type_id_to_category_name(type_id)
            if case == 4 and category == 'Drone':
                fit['drones'].append({
                    "type_name": type_name,
                    "type_id": type_id,
                    "quantity": int(quantity[1:]) if quantity else None,
                })
            elif case == 4 and category == 'Implant':
                fit['drones'].append({
                    "type_name": type_name,
                    "type_id": type_id,
                    "quantity": int(quantity[1:]) if quantity else None,
                })
            elif case == 4:
                fit['cargo'].append({
                    "type_name": type_name,
                    "type_id": type_id,
                    "quantity":  int(quantity[1:]) if quantity else None,
                })
            else:
                fit[cases[case]].append({
                    "type_name": type_name,
                    "type_id": type_id,
                    "quantity": quantity if quantity else None,
                })
            
        return fit

class EveSkillPlan(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField(blank=True, null=True)
    skills = models.TextField()
    tags = models.ManyToManyField("EveDoctrineManagerTag", blank=True)
    doctrines = models.ManyToManyField("EveDoctrine", blank=True)
    roles = models.ManyToManyField("EveDoctrineRole", blank=True)

    def get_required_skills(self):
        cleaned_skill_list = []
        # clean skills from "SKILL V" format to "SKILL 1"
        skills = self.skills
        skills = skills.replace("<p>", "").replace("</p>", "")
        skills = skills.replace("<br>", "\n")
        for skill in filter(None, skills.split("\n")):
            skill_name = " ".join(skill.split(" ")[:-1])
            skill_level = roman.fromRoman("".join(skill.split(" ")[-1:]).rstrip("\n\r"))
            cleaned_skill_list.append(f"{skill_name} {skill_level}")
        return EveSkillList.from_list(cleaned_skill_list)

    def __str__(self):
        return self.name    


"""
Grouping models
Used to group fittings and doctrines for users and clarity.
"""
class EveRequiredSkill(models.Model):
    name = models.CharField(
        max_length=64, choices=get_skill_names_from_static_dump())
    level = models.IntegerField(
        validators=[MaxValueValidator(5), MinValueValidator(1)])
    skill_for = models.ForeignKey("EveSkillPlan", on_delete=models.CASCADE)

class EveDoctrineRole(models.Model):
    name = models.CharField(max_length=128)
    icon = models.URLField()
    color = models.CharField(max_length=32, choices=bootstrap_color_choices)


    def __str__(self):
        return self.name

class EveDoctrineCategory(models.Model):
    name = models.CharField(max_length=128)
    icon = models.URLField()
    color = models.CharField(max_length=32, choices=bootstrap_color_choices)

    def __str__(self):
        return self.name

class EveDoctrineManagerTag(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


