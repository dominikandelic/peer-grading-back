from datetime import date
from ninja import Schema
from ninja_jwt.schema import TokenObtainPairInputSchema


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


class MyTokenObtainPairOutSchema(Schema):
    refresh: str
    access: str
    user: UserResponse


class MyTokenObtainPairSchema(TokenObtainPairInputSchema):
    def output_schema(self):
        out_dict = self.dict(exclude={"password"})
        out_dict.update(user=UserResponse.from_orm(self._user))
        return MyTokenObtainPairOutSchema(**out_dict)
