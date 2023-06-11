from datetime import date
from ninja import Schema


class UserResponse(Schema):
    id: int
    username: str
    first_name: str
    last_name: str
    is_student: bool
    is_teacher: bool


class CourseResponse(Schema):
    id: int
    name: str


class TaskResponse(Schema):
    id: int
    name: str
