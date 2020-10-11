
import logging
from .defaults import *


class User(object):
    def __init__(self, session):
        self.session = session
    def get_departments(self):
        raise NotImplementedError()
    def get_departments_by_id(self, department_id):
        raise NotImplementedError()
    def get_groups(self):
        raise NotImplementedError()
    def get_group_by_id(self, group_id):
        raise NotImplementedError()
    def get_users(self):
        raise NotImplementedError()
    def get_user_by_id(self, user_id):
        raise NotImplementedError()
    def create_user(self, user):
        raise NotImplementedError()
    def delete_users(self, users):
        raise NotImplementedError()
    def update_user(self, user):
        raise NotImplementedError()
    def delete_user_by_id(self, user):
        raise NotImplementedError()


LOGGER = logging.getLogger(__name__)
