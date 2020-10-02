from datetime import date

import pytest
from model_bakery import baker

from huscy.subjects.services import create_subject

pytestmark = pytest.mark.django_db


@pytest.mark.freeze_time('2020-01-01')
@pytest.mark.parametrize('date_of_birth,is_child', [
    (date(2000, 1, 1), False),
    (date(2001, 12, 31), False),
    (date(2002, 1, 1), False),
    (date(2002, 1, 2), True),
    (date(2003, 1, 1), True),
])
def test_is_child(date_of_birth, is_child):
    contact = baker.make('subjects.Contact', date_of_birth=date_of_birth)

    subject = create_subject(contact)

    assert subject.is_child is is_child


@pytest.mark.parametrize('is_patient', [True, False])
def test_is_patient(contact, is_patient):
    subject = create_subject(contact, is_patient=is_patient)

    assert subject.is_patient is is_patient
