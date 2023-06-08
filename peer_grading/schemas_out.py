from datetime import date
from ninja import Schema


class StudentOut(Schema):
    username: str
    password: str
    first_name: str
    last_name: str


class TeacherOut(Schema):
    username: str
    password: str
    first_name: str
    last_name: str
