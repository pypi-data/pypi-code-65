from django.test import TestCase

from wagtailperson.models import Person


class PersonTasteCase(TestCase):
    """Test the Person model"""
    def setUp(self):
        """Setup the database"""
        self.person_name = 'Alice and Bob'
        self.person_name_slug = 'alice-and-bob'
        
        self.person = Person(
            name=self.person_name,
        )
        self.person.save()

    def test_person_name_slug(self):
        """Test the slugify name of a person"""
        self.assertEqual(
            self.person.name_slug,
            self.person_name_slug,
        )
