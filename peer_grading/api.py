import json
from django.db import transaction
from django.utils import timezone
from dateutil import parser
from ninja import File, Schema, UploadedFile
from typing import List
from ninja.errors import HttpError
from ninja_extra import NinjaExtraAPI, api_controller, route
from django.contrib.auth.hashers import make_password
from ninja_jwt.controller import TokenObtainPairController
from peer_grading.models import (
    Course,
    Grading,
    Student,
    Submission,
    Task,
    Teacher,
    User,
)
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
from peer_grading.schemas_out import (
    CourseResponse,
    MyTokenObtainPairOutSchema,
    MyTokenObtainPairSchema,
    SubmissionResponse,
    TaskResponse,
    UserResponse,
)
import orjson
from ninja.renderers import BaseRenderer


class ORJSONRenderer(BaseRenderer):
    media_type = "application/json"

    def render(self, request, data, *, response_status):
        return orjson.dumps(data)


@api_controller("/token", tags=["Auth"])
class MyTokenObtainPairController(TokenObtainPairController):
    @route.post(
        "/pair", response=MyTokenObtainPairOutSchema, url_name="token_obtain_pair"
    )
    def obtain_token(self, user_token: MyTokenObtainPairSchema):
        return user_token.output_schema()


api = NinjaExtraAPI(renderer=ORJSONRenderer())
api.register_controllers(MyTokenObtainPairController)


class Error(Schema):
    message: str


class StudentNotEnrolledError(Exception):
    pass


# initializing handler


@api.exception_handler(StudentNotEnrolledError)
def service_unavailable(request, exc):
    return api.create_response(
        request,
        {"message": "Student not enrolled to this course"},
        status=409,
    )


@api.get("/profile", auth=JWTAuth(), response=UserResponse)
def get_profile(request):
    return request.user


@api.put("/profile", auth=JWTAuth())
def update_profile(request, payload: UpdateProfileRequest):
    user = User.objects.get(pk=request.user.id)
    user.first_name = payload.first_name
    user.last_name = payload.last_name
    user.save()


@api.get("/users/{user_id}", response=UserResponse, auth=JWTAuth())
def get_user(request, user_id):
    return User.objects.get(pk=user_id)


@api.get("/teachers", auth=JWTAuth(), response=List[UserResponse])
def get_teachers(request):
    return Teacher.objects.get_queryset()


@api.get(
    "/teachers/{teacher_id}/courses/",
    response=List[CourseResponse],
    auth=JWTAuth(),
)
def get_teacher_courses(request, teacher_id):
    teacher = Teacher.objects.get(pk=teacher_id)
    return list(teacher.course_set.all())


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


@api.get(
    "/students/{student_id}/submissions/",
    response=List[SubmissionResponse],
    auth=JWTAuth(),
)
def get_student_submissions(request, student_id):
    student = Student.objects.get(pk=student_id)
    return list(Submission.objects.filter(student=student))


@api.get(
    "/students/{student_id}/courses/",
    response=List[CourseResponse],
    auth=JWTAuth(),
)
def get_student_courses(request, student_id):
    student = Student.objects.get(pk=student_id)
    return list(student.course_set.all())


@api.get(
    "/students/{student_id}/submissions/{submission_id}",
    response=SubmissionResponse,
    auth=JWTAuth(),
)
def get_student_submission(request, student_id, submission_id):
    return Submission.objects.get(pk=submission_id)


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
    task = Task.objects.get(pk=id)
    return task


@api.get(
    "/tasks/{task_id}/{student_username}/has-submitted/",
    auth=JWTAuth(),
)
def has_student_submitted(request, student_username, task_id):
    student = Student.objects.get(username=student_username)
    task = Task.objects.get(pk=task_id)
    return Submission.objects.filter(student=student, submission_task=task).count() > 0


@api.get(
    "/tasks/{task_id}/{student_username}/submission",
    auth=JWTAuth(),
    response=SubmissionResponse,
)
def get_student_submission(request, student_username, task_id):
    student = Student.objects.get(username=student_username)
    task = Task.objects.get(pk=task_id)
    return Submission.objects.filter(student=student, submission_task=task).first()


@api.get("/tasks", response=List[TaskResponse], auth=JWTAuth())
def get_active_tasks(request):
    if request.user.is_teacher:
        teacher = Teacher.objects.get(pk=request.user.id)
        tasks = Task.objects.filter(course__teacher=teacher)
        return list(tasks)
    if request.user.is_student:
        student = Student.objects.get(pk=request.user.id)
        tasks = Task.objects.filter(course__students__in=[student])
        return list(tasks)
    else:
        return list(Task.objects.all())


@api.post("/tasks", auth=JWTAuth(), response={409: Error, 200: str})
def create_task(request, payload: CreateTaskRequest):
    if request.user.is_teacher:
        course = Course.objects.get(pk=payload.course_id)
        if course.teacher.id == request.user.id:
            with transaction.atomic():
                task = Task.objects.create(name=payload.name, course=course)
                task.save()
                tz = timezone.get_current_timezone()
                deadline = parser.parse(payload.deadline)
                deadline = timezone.make_aware(deadline, tz, True)
                grading = Grading.objects.create(
                    task=task,
                    instructions=payload.instructions,
                    submissions_number=payload.submissions_number,
                    deadline=deadline,
                )
                grading.save()
                return "OK"
        else:
            return 409, {"message": "Username taken"}
    else:
        return 409, {"message": "Username taken"}


@api.get(
    "/task-submissions/{task_id}", response=List[SubmissionResponse], auth=JWTAuth()
)
def get_task_submissions(request, task_id):
    task = Task.objects.get(pk=task_id)
    return Submission.objects.filter(submission_task=task)


@api.get("/submissions/{submission_id}", response=SubmissionResponse, auth=JWTAuth())
def get_submission(request, submission_id):
    return Submission.objects.get(pk=submission_id)


@api.post("/submissions", auth=JWTAuth())
def create_submission(
    request, details: CreateSubmissionRequest, file: UploadedFile = File(...)
):
    student = Student.objects.get(pk=request.user.id)
    task = Task.objects.get(pk=details.task_id)
    # Check if student is enrolled in the course
    if student.course_set.filter(id=task.course.id).exists():
        Submission.objects.create(file=file, submission_task=task, student=student)
    else:
        raise StudentNotEnrolledError()
