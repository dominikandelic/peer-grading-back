from datetime import datetime
from ninja import Schema


class RegisterStudentRequest(Schema):
    username: str
    password: str
    first_name: str
    last_name: str


class RegisterTeacherRequest(Schema):
    username: str
    password: str
    first_name: str
    last_name: str


class CreateCourseRequest(Schema):
    name: str
    teacher_id: int


class UpdateProfileRequest(Schema):
    first_name: str
    last_name: str


class CreateTaskRequest(Schema):
    name: str
    course_id: int
    instructions: str
    submissions_number: int
    deadline: str


class CreateSubmissionRequest(Schema):
    task_id: int


class EnrollStudentRequest(Schema):
    student_id: int
