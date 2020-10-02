from datetime import date

import pytest
from model_bakery import baker

pytestmark = pytest.mark.django_db


@pytest.mark.freeze_time('2000-01-01')
@pytest.mark.parametrize('date_of_birth,age_in_months', [
    (date(1999, 10, 1), 3),
    (date(1998, 1, 1), 24),
    (date(1998, 1, 2), 23),
    (date(1980, 1, 1), 240),
])
def test_age_in_months(date_of_birth, age_in_months):
    subject = baker.prepare('subjects.Subject', contact__date_of_birth=date_of_birth)

    assert subject.age_in_months == age_in_months


@pytest.mark.freeze_time('2000-01-01')
@pytest.mark.parametrize('date_of_birth,age_in_years', [
    (date(1999, 10, 1), 0),
    (date(1998, 1, 1), 2),
    (date(1998, 1, 2), 1),
    (date(1980, 1, 1), 20),
])
def test_age_in_years(date_of_birth, age_in_years):
    subject = baker.prepare('subjects.Subject', contact__date_of_birth=date_of_birth)

    assert subject.age_in_years == age_in_years


def test_is_active_with_inactivity_reference(subject, inactivity):
    assert subject.is_active is False


def test_is_active_without_inactivity_reference(subject):
    assert subject.is_active is True


def test_is_child_with_child_reference(subject):
    baker.make('subjects.Child', subject=subject)

    assert subject.is_child is True


def test_is_child_without_child_reference(subject):
    assert subject.is_child is False


def test_is_patient_with_patient_reference(subject):
    baker.make('subjects.Patient', subject=subject)

    assert subject.is_patient is True


def test_is_patient_without_patient_reference(subject):
    assert subject.is_patient is False
