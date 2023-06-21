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
    teacher: UserResponse = None


class TaskResponse(Schema):
    id: int
    name: str
    course: CourseResponse


class SubmissionResponse(Schema):
    id: int
    file: str
    student: UserResponse
    created_at: date
