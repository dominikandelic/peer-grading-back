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
