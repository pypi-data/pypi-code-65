import unittest

from python_deploy_test import person


class TestPerson(unittest.TestCase):
    def test_person_builder(self):
        my_person = person.Person('Ben', 31)
        self.assertEqual('Ben', my_person.name)
        self.assertEqual(31, my_person.age)


if __name__ == '__main__':
    unittest.main()
