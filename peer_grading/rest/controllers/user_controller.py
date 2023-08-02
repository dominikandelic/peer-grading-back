from typing import List

from django.contrib.auth.hashers import make_password
from ninja_extra import api_controller, route
from ninja_jwt.authentication import JWTAuth

from peer_grading.models import User, Teacher, Student
from peer_grading.rest.exceptions.exceptions import BadRequestException
from peer_grading.rest.schemas.schemas_in import UpdateProfileRequest, RegisterStudentRequest, RegisterTeacherRequest
from peer_grading.rest.schemas.schemas_out import UserResponse


@api_controller(tags=["User"])
class UserController:
    @route.get("/users/{user_id}", response=UserResponse, auth=JWTAuth())
    def get_user(self, user_id):
        return User.objects.get(pk=user_id)

    @route.get("/profile", auth=JWTAuth(), response=UserResponse)
    def get_profile(self):
        return self.context.request.auth

    @route.get("/teachers", auth=JWTAuth(), response=List[UserResponse])
    def get_teachers(self):
        return Teacher.objects.get_queryset()

    @route.get("/students", auth=JWTAuth(), response=List[UserResponse])
    def get_students(self):
        return Student.objects.get_queryset()

    @route.post("/register/student")
    def register_student(self, payload: RegisterStudentRequest):
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
            raise BadRequestException(detail="Došlo je do pogreške", code="REGISTER_ERROR")
        return "OK"

    @route.post("/register/teacher")
    def register_teacher(self, payload: RegisterTeacherRequest):
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
            raise BadRequestException(detail="Došlo je do pogreške", code="REGISTER_ERROR")
        return "OK"

    @route.put("/profile", auth=JWTAuth())
    def update_profile(self, payload: UpdateProfileRequest):
        user = User.objects.get(pk=self.context.request.auth.id)
        user.first_name = payload.first_name
        user.last_name = payload.last_name
        user.save()

    @route.delete("/users/{user_id}", auth=JWTAuth())
    def delete_user(self, user_id: int):
        if self.context.request.auth.is_superuser or self.context.request.auth.id == user_id:
            user = User.objects.get(pk=user_id)
            user.delete()
        else:
            raise BadRequestException(detail="Došlo je do pogreške", code="DELETE_ERROR")
