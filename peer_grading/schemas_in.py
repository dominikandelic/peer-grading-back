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


class CreateSubmissionRequest(Schema):
    task_id: int
