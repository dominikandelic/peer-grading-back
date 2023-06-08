from ninja import Schema
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_extra import NinjaExtraAPI
from django.contrib.auth.hashers import make_password
from peer_grading.models import Student, Teacher
from ninja_jwt.authentication import JWTAuth
from peer_grading.schemas_in import RegisterStudentRequest, RegisterTeacherRequest

api = NinjaExtraAPI()
api.register_controllers(NinjaJWTDefaultController)


class Error(Schema):
    message: str


@api.get("/me", auth=JWTAuth())
def me(request):
    if request.user.is_teacher:
        return "Teacher"
    elif request.user.is_student:
        return "Student"
    else:
        return "Superuser?"


@api.post("/register/student", response={409: Error, 200: str})
def register_student(request, payload: RegisterStudentRequest):
    try:
        Student.objects.create(
            username=payload.username,
            password=make_password(payload.password),
            first_name=payload.first_name,
            last_name=payload.last_name,
            is_active=True,
            is_student=True,
        )
    except:
        return 409, {"message": "Username taken"}
    return "OK"


@api.post("/register/teacher", response={409: Error, 200: str})
def register_teacher(request, payload: RegisterTeacherRequest):
    try:
        Teacher.objects.create(
            username=payload.username,
            password=make_password(payload.password),
            first_name=payload.first_name,
            last_name=payload.last_name,
            is_active=True,
            is_teacher=True,
        )
    except:
        return 409, {"message": "Username taken"}
    return "OK"
