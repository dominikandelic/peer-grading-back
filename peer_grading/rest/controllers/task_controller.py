from typing import List

from dateutil import parser
from django.db import transaction
from django.utils import timezone
from ninja_extra import api_controller, route
from ninja_jwt.authentication import JWTAuth

from peer_grading.models import Task, Student, Teacher, Course, Grading, GradingStatus, Submission, GradingResult, \
    StudentGradingStatus
from peer_grading.rest.exceptions.exceptions import BadRequestException
from peer_grading.rest.schemas.schemas_in import UpdateTaskRequest, CreateTaskRequest, UpdateGradingStatus
from peer_grading.rest.schemas.schemas_out import TaskResponse


@api_controller(auth=JWTAuth(), tags=["Task"])
class TaskController:
    @route.get("/tasks", response=List[TaskResponse])
    def get_active_tasks(self):
        if self.context.request.auth.is_teacher:
            teacher = Teacher.objects.get(pk=self.context.request.auth.id)
            tasks = Task.objects.filter(course__teacher=teacher)
            return list(tasks)
        if self.context.request.auth.is_student:
            student = Student.objects.get(pk=self.context.request.auth.id)
            tasks = Task.objects.filter(course__students__in=[student])
            return list(tasks)
        else:
            return list(Task.objects.all())

    @route.get("/tasks/{task_id}", response=TaskResponse)
    def get_task(self, task_id: int):
        task = Task.objects.get(pk=task_id)
        return task

    @route.post("/tasks", response={200: str})
    def create_task(self, payload: CreateTaskRequest):
        if self.context.request.auth.is_teacher or self.context.request.auth.is_superuser:
            course = Course.objects.get(pk=payload.course_id)
            if course.teacher.id == self.context.request.auth.id or self.context.request.auth.is_superuser:
                with transaction.atomic():
                    tz = timezone.get_current_timezone()
                    deadline = parser.parse(payload.deadline)
                    deadline = timezone.make_aware(deadline, tz, True)
                    task = Task.objects.create(
                        name=payload.name, course=course, deadline=deadline
                    )
                    task.save()
                    grading = Grading.objects.create(
                        task=task,
                        instructions=payload.instructions,
                        submissions_number=payload.submissions_number,
                    )
                    grading.save()
                    return "OK"
            else:
                raise BadRequestException(detail="An error has occurred", code="UPDATE_ERROR")
        else:
            raise BadRequestException(detail="An error has occurred", code="UPDATE_ERROR")

    @route.put("/tasks/{task_id}", response={200: str})
    def update_task(self, payload: UpdateTaskRequest, task_id: int):
        if self.context.request.auth.is_teacher or self.context.request.auth.is_superuser:
            task = Task.objects.get(pk=task_id)
            if task.course.teacher.id == self.context.request.auth.id or self.context.request.auth.is_superuser:
                with transaction.atomic():
                    task.name = payload.name
                    tz = timezone.get_default_timezone()
                    deadline = parser.parse(payload.deadline)
                    deadline = timezone.make_aware(deadline, tz, True)
                    task.deadline = deadline
                    task.save()
                    task.grading.instructions = payload.instructions
                    task.grading.submissions_number = payload.submissions_number
                    task.deadline = deadline
                    task.grading.save()
                    return "OK"
            else:
                raise BadRequestException(detail="An error has occurred", code="UPDATE_ERROR")
        else:
            raise BadRequestException(detail="An error has occurred", code="UPDATE_ERROR")

    @route.patch(
        "/tasks/{task_id}/grading-status", response={200: str}
    )
    def update_grading_status(self, payload: UpdateGradingStatus, task_id):
        if self.context.request.auth.is_teacher or self.context.request.auth.is_superuser:
            task = Task.objects.get(pk=task_id)
            if task.course.teacher.id == self.context.request.auth.id or self.context.request.auth.is_superuser:
                with transaction.atomic():
                    task.grading.status = payload.status
                    task.grading.save()
                    if task.grading.status == GradingStatus.FINISHED:
                        submissions = Submission.objects.filter(submission_task=task).all()
                        for submission in submissions:
                            total_score = calculate_submission_total_score(submission)
                            GradingResult.objects.create(submission=submission, total_score=total_score)
                    return "OK"
            else:
                raise BadRequestException(detail="An error has occurred", code="UPDATE_ERROR")
        else:
            raise BadRequestException(detail="An error has occurred", code="UPDATE_ERROR")

    @route.delete("/tasks/{task_id}")
    def delete_task(self, task_id: int):
        if self.context.request.auth.is_teacher or self.context.request.auth.is_superuser:
            task = Task.objects.get(pk=task_id)
            task.delete()
        else:
            raise BadRequestException(detail="An error has occurred", code="DELETE_ERROR")


def calculate_submission_total_score(submission: Submission):
    return sum([x.grade for x in submission.submissiongrade_set.filter(status=StudentGradingStatus.DONE).all()])
