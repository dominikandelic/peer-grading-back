from datetime import datetime
from typing import List

from django.utils import timezone
from ninja import File, UploadedFile
from ninja_extra import api_controller, route
from ninja_jwt.authentication import JWTAuth

from peer_grading.models import Task, Submission, Student, GradingStatus
from peer_grading.rest.exceptions.exceptions import BadRequestException
from peer_grading.rest.schemas.schemas_in import CreateSubmissionRequest
from peer_grading.rest.schemas.schemas_out import SubmissionResponse


@api_controller(auth=JWTAuth(), tags=["Submission"])
class SubmissionController:
    @route.get(
        "/task-submissions/{task_id}", response=List[SubmissionResponse], auth=JWTAuth(), tags=["Submission"]
    )
    def get_task_submissions(self, task_id):
        task = Task.objects.get(pk=task_id)
        return task.submission_set.all()

    @route.get("/submissions/{submission_id}", response=SubmissionResponse, auth=JWTAuth(), tags=["Submission"])
    def get_submission(self, submission_id):
        return Submission.objects.get(pk=submission_id)

    @route.get(
        "/tasks/{task_id}/own-submission",
        auth=JWTAuth(),
        response=SubmissionResponse,
        tags=["Submission"]
    )
    def get_own_submission(self, task_id: int):
        student = Student.objects.get(pk=self.context.request.auth.id)
        task = Task.objects.get(pk=task_id)
        return student.submission_set.filter(submission_task=task).first()

    @route.get(
        "/tasks/{task_id}/student/has-submitted/",
        auth=JWTAuth(),
        tags=["Submission"]
    )
    def has_student_submitted(self, task_id: int):
        student = Student.objects.get(pk=self.context.request.auth.id)
        task = Task.objects.get(pk=task_id)
        return Submission.objects.filter(student=student, submission_task=task).count() > 0

    @route.get(
        "/students/{student_id}/submissions/",
        response=List[SubmissionResponse],
        auth=JWTAuth(),
        tags=["Submission"]
    )
    def get_student_submissions(self, student_id):
        student = Student.objects.get(pk=student_id)
        return list(Submission.objects.filter(student=student))

    @route.get(
        "/students/{student_id}/submissions/{submission_id}",
        response=SubmissionResponse,
        auth=JWTAuth(),
        tags=["Submission"]
    )
    def get_student_submission(self, student_id, submission_id):
        return Submission.objects.get(pk=submission_id)

    @route.post("/submissions", auth=JWTAuth(), tags=["Submission"])
    def create_submission(
            self, details: CreateSubmissionRequest, file: UploadedFile = File(...)
    ):
        student = Student.objects.get(pk=self.context.request.auth.id)
        task = Task.objects.get(pk=details.task_id)
        # Check if student is enrolled in the course
        if (
                student.course_set.filter(id=task.course.id).exists()
                and task.grading.status == GradingStatus.STANDBY
                and datetime.now(tz=timezone.get_default_timezone()) <= task.deadline
        ):
            Submission.objects.create(file=file, submission_task=task, student=student)
        else:
            raise BadRequestException(detail="You cannot submit anymore", code="CREATE_ERROR")
