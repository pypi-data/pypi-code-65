from datetime import date

import pytest
from model_bakery import baker

from huscy.subjects.services import update_subject

pytestmark = pytest.mark.django_db


@pytest.mark.freeze_time('2020-01-01')
@pytest.mark.parametrize('date_of_birth, is_child', [
    (date(2001, 1, 1), False),
    (date(2001, 12, 31), False),
    (date(2002, 1, 1), False),
    (date(2002, 1, 2), True),
    (date(2003, 1, 1), True),
])
def test_is_child(date_of_birth, is_child):
    contact = baker.make('subjects.Contact', date_of_birth=date_of_birth)
    subject = baker.make('subjects.Subject', contact=contact)

    assert subject.is_child is False

    update_subject(subject, is_patient=False)

    assert subject.is_child is is_child


@pytest.mark.freeze_time('2020-01-01')
@pytest.mark.parametrize('date_of_birth', [
    date(2001, 1, 1),
    date(2001, 12, 31),
    date(2002, 1, 1),
    date(2002, 1, 2),
    date(2003, 1, 1),
])
def test_is_child_while_subject_is_already_a_child(date_of_birth):
    contact = baker.make('subjects.Contact', date_of_birth=date_of_birth)
    subject = baker.make('subjects.Subject', contact=contact)
    baker.make('subjects.Child', subject=subject)

    assert subject.is_child is True

    update_subject(subject, is_patient=False)

    assert subject.is_child is True


def test_is_patient_is_true(subject):
    assert subject.is_patient is False

    update_subject(subject, is_patient=True)

    assert subject.is_patient is True


def test_is_patient_is_true_but_subject_is_already_a_patient(patient, subject):
    assert subject.is_patient is True

    update_subject(subject, is_patient=True)

    assert subject.is_patient is True


def test_is_patient_is_false(subject):
    assert subject.is_patient is False

    update_subject(subject, is_patient=False)

    assert subject.is_patient is False


def test_is_patient_is_false_but_subject_is_a_patient(patient, subject):
    assert subject.is_patient is True

    update_subject(subject, is_patient=False)

    assert subject.is_patient is False
