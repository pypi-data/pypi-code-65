from viewmodel import BaseView, IdField, IntField, TxtField
from viewmodel.viewFields import ObjListField, TxtListField, viewModelDB

database = viewModelDB.baseDB.db


class Student(BaseView):
    models_ = database.Students
    id = IdField(cases={})  # , name = '_id')
    name = TxtField()
    course = TxtField(value='engineering')
    course_year = IntField()
    facultyList = ObjListField(label="A list of faculties")
    courseList = TxtListField(label="A list of courses")


class StudentWithNameFieldWithAlias(BaseView):
    models_ = database.Students
    id = IdField(cases={})  # , name = '_id')
    first_name = TxtField(src='.name')  # alias used for 'name' in collection
    course = TxtField(value='engineering')
    course_year = IntField()


class Courses(BaseView):
    models_ = database.Courses
    id = IdField(cases={})  # , name = '_id')
    name = TxtField()
    course = TxtField(value='engineering')
    course_year = IntField()
