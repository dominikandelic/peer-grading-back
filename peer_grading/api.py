from ninja import File, Schema, UploadedFile
from typing import List
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_extra import NinjaExtraAPI
from django.contrib.auth.hashers import make_password
from peer_grading.models import Course, Student, Submission, Task, Teacher, User
from ninja_jwt.authentication import JWTAuth
from peer_grading.schemas_in import (
    CreateCourseRequest,
    CreateSubmissionRequest,
    CreateTaskRequest,
    EnrollStudentRequest,
    RegisterStudentRequest,
    RegisterTeacherRequest,
    UpdateProfileRequest,
)
from peer_grading.schemas_out import CourseResponse, TaskResponse, UserResponse
import orjson
from ninja.renderers import BaseRenderer


class ORJSONRenderer(BaseRenderer):
    media_type = "application/json"

    def render(self, request, data, *, response_status):
        return orjson.dumps(data)


api = NinjaExtraAPI(renderer=ORJSONRenderer())
api.register_controllers(NinjaJWTDefaultController)


class Error(Schema):
    message: str


@api.get("/profile", auth=JWTAuth(), response=UserResponse)
def get_profile(request):
    return request.user


@api.put("/profile", auth=JWTAuth())
def update_profile(request, payload: UpdateProfileRequest):
    user = User.objects.get(pk=request.user.id)
    user.first_name = payload.first_name
    user.last_name = payload.last_name
    user.save()


@api.get("/users", auth=JWTAuth())
def me(request):
    if request.user.is_teacher:
        return request.user.id
    elif request.user.is_student:
        return "Student"
    else:
        return "Superuser?"


@api.get("/teachers", auth=JWTAuth(), response=List[UserResponse])
def get_teachers(request):
    return Teacher.objects.get_queryset()


@api.get("/students", auth=JWTAuth(), response=List[UserResponse])
def get_students(request):
    return Student.objects.get_queryset()


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


@api.get("/courses", response=List[CourseResponse], auth=JWTAuth())
def get_courses(request):
    courses = Course.objects.get_queryset()
    return list(courses)


@api.get("/courses/{id}", response=CourseResponse, auth=JWTAuth())
def get_course(request, id: int):
    return Course.objects.get(pk=id)


@api.get("/courses/{course_id}/tasks/", response=List[TaskResponse], auth=JWTAuth())
def get_course_tasks(request, course_id: int):
    course = Course.objects.get(pk=course_id)
    return course.task_set.all()


@api.get("/courses/{course_id}/students/", response=List[UserResponse], auth=JWTAuth())
def get_enrolled_students(request, course_id: int):
    course = Course.objects.get(pk=course_id)
    return course.students.all()


@api.post("/courses", response={409: Error, 200: str}, auth=JWTAuth())
def create_course(request, payload: CreateCourseRequest):
    try:
        teacher = Teacher.objects.get(pk=payload.teacher_id)
        Course.objects.create(name=payload.name, teacher=teacher)
    except:
        return 409, {"message": "An error has ocurred"}
    return "OK"


@api.post(
    "/courses/{course_id}/enroll-students",
    response={409: Error, 200: str},
    auth=JWTAuth(),
)
def create_course(request, payload: EnrollStudentRequest, course_id: int):
    try:
        student = Student.objects.get(pk=payload.student_id)
        course = Course.objects.get(pk=course_id)
        course.students.add(student)
        course.save()
    except:
        return 409, {"message": "An error has ocurred"}
    return "OK"


@api.get("/tasks/{id}", response=TaskResponse, auth=JWTAuth())
def get_task(request, id: int):
    return Task.objects.get(pk=id)


@api.post("/tasks", response={409: Error, 200: str}, auth=JWTAuth())
def create_task(request, payload: CreateTaskRequest):
    course = Course.objects.get(pk=payload.course_id)
    print(course.name)
    Task.objects.create(name=payload.name, course=course)
    return "OK"


@api.post("/submissions", auth=JWTAuth())
def create_submission(
    request, details: CreateSubmissionRequest, file: UploadedFile = File(...)
):
    task = Task.objects.get(pk=details.task_id)
    student = Student.objects.get(pk=request.user.id)
    submission = Submission.objects.create(
        file=file, submission_task=task, student=student
    )
    print(submission)
