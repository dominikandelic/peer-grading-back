from datetime import date, datetime
from ninja import Schema
from ninja_jwt.schema import TokenObtainPairInputSchema

from peer_grading.models import StudentGradingStatus


class UserResponse(Schema):
    id: int
    username: str
    first_name: str
    last_name: str
    is_student: bool
    is_teacher: bool
    is_superuser: bool


class GradingResponse(Schema):
    status: str
    instructions: str
    submissions_number: int


class CourseResponse(Schema):
    id: int
    name: str
    teacher: UserResponse = None


class TaskResponse(Schema):
    id: int
    name: str
    grading: GradingResponse
    course: CourseResponse
    created_at: datetime
    deadline: datetime


class SubmissionResponse(Schema):
    id: int
    file: str
    student: UserResponse
    created_at: datetime
    submission_task: TaskResponse


class GradingResultResponse(Schema):
    id: int
    total_score: int
    submission: SubmissionResponse


class SubmissionGradeResponse(Schema):
    id: int
    grader: UserResponse
    grade: int
    submission: SubmissionResponse
    status: StudentGradingStatus


class MyTokenObtainPairOutSchema(Schema):
    refresh: str
    access: str
    user: UserResponse


class MyTokenObtainPairSchema(TokenObtainPairInputSchema):
    def output_schema(self):
        out_dict = self.dict(exclude={"password"})
        out_dict.update(user=UserResponse.from_orm(self._user))
        return MyTokenObtainPairOutSchema(**out_dict)
