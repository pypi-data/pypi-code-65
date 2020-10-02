import pytest

from django.contrib.auth.models import Permission
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_201_CREATED, HTTP_403_FORBIDDEN

from huscy.subjects.models import Note

pytestmark = pytest.mark.django_db


def test_notes_url(subject):
    url = reverse('note-list', kwargs=dict(subject_pk=subject.pk))
    assert url == f'/api/subjects/{subject.pk}/notes/'


def test_admin_user_can_create_note(admin_client, admin_user, subject):
    response = create_note(admin_client, subject)

    assert response.status_code == HTTP_201_CREATED
    assert_note_created(admin_user)


def test_user_with_permission_can_create_note(client, user, subject):
    change_permission = Permission.objects.get(codename='change_subject')
    user.user_permissions.add(change_permission)

    response = create_note(client, subject)

    assert response.status_code == HTTP_201_CREATED, response.json()
    assert_note_created(user)


def test_user_without_permission_cannot_create_note(client, user, subject):
    response = create_note(client, subject)

    assert response.status_code == HTTP_403_FORBIDDEN


def test_anonymous_user_cannot_create_note(anonymous_client, subject):
    response = create_note(anonymous_client, subject)

    assert response.status_code == HTTP_403_FORBIDDEN


def create_note(client, subject):
    return client.post(
        reverse('note-list', kwargs=dict(subject_pk=subject.pk)),
        data=dict(
            text='here is comment',
            option=255,
        ),
        format='json',
    )


def assert_note_created(creator):
    assert Note.objects.all().count() == 1
    n = Note.objects.all().first()
    assert n.option == 255
    assert n.text == 'here is comment'
    assert n.creator == creator
