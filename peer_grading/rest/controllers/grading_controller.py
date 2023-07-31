from typing import List

from django.db.models import Count
from django.db.models.functions import Length
from ninja_extra import api_controller, route
from ninja_jwt.authentication import JWTAuth

from peer_grading.models import Submission, Student, Task, SubmissionGrade, StudentGradingStatus, GradingResult
from peer_grading.rest.exceptions.exceptions import BadRequestException
from peer_grading.rest.schemas.schemas_in import GradeSubmissionRequest
from peer_grading.rest.schemas.schemas_out import SubmissionResponse, GradingResultResponse, SubmissionGradeResponse


@api_controller(tags=["Grading"], auth=JWTAuth())
class GradingController:
    @route.get("/grading/{task_id}", response=List[SubmissionResponse])
    def get_submissions_for_grading(self, task_id: int):
        task = Task.objects.get(pk=task_id)
        # Define the number of submissions to filter
        n = task.grading.submissions_number
        student = Student.objects.get(pk=self.context.request.auth.id)
        has_submission_grade = SubmissionGrade.objects.filter(grader=student, submission__submission_task=task).exists()
        if has_submission_grade:
            # Find all submissions with SubmissionGrade for the task and in "IN_PROGRESS" status
            submissions_with_in_progress_grade = Submission.objects.filter(
                submissiongrade__status=StudentGradingStatus.IN_PROGRESS,
                submissiongrade__grader__submission__submission_task=task,
                submissiongrade__grader=student
            )
            return submissions_with_in_progress_grade
        # Get all submissions for the task, excluding the student's own submission
        total_submissions = task.submission_set.exclude(student=student)
        # Check if the total number of submissions is less than or equal to n
        if total_submissions.count() <= n:
            # If there are fewer or equal submissions than n, use all the submissions
            filtered_submissions = total_submissions
        else:
            # Sort the submissions by the number of grades received and introduce random ordering for equal num_grades
            sorted_submissions = (
                total_submissions
                .filter(submission_task=task)
                .annotate(num_grades=Count('submissiongrade'))
                .annotate(random_order=Length('num_grades'))
                .order_by('num_grades', 'random_order', 'id')
            )
            # Select the top n submissions from the sorted list
            filtered_submissions = sorted_submissions[:n]

        for submission in filtered_submissions:
            submission_grade = SubmissionGrade.objects.create(grader=student, submission=submission)
            submission_grade.save()

        return filtered_submissions

    @route.get("/grading/{task_id}/results", response=List[GradingResultResponse])
    def get_task_grading_results(self, task_id):
        task = Task.objects.get(pk=task_id)
        return GradingResult.objects.filter(submission__submission_task=task).order_by('-total_score')

    @route.get("/grading/submissions/{submission_id}/results", response=List[SubmissionGradeResponse])
    def get_submission_grading_results(self, submission_id):
        submission = Submission.objects.get(pk=submission_id)
        return submission.submissiongrade_set.exclude(status=StudentGradingStatus.IN_PROGRESS).order_by('-grade')

    @route.get("/grading/{task_id}/has-graded")
    def has_already_graded_submission(self, task_id):
        task = Task.objects.get(pk=task_id)
        return SubmissionGrade.objects.filter(grader=self.context.request.auth, submission__submission_task=task,
                                              status=StudentGradingStatus.DONE).exists()

    @route.put("/grading/{task_id}")
    def grade_submissions(self, payload: List[GradeSubmissionRequest], task_id: int):
        if has_valid_grades_sum([x.grade for x in payload], len(payload)):
            for request in payload:
                submission = Submission.objects.get(pk=request.submission_id)
                student = Student.objects.get(pk=self.context.request.auth)
                submission_grade = SubmissionGrade.objects.get(submission=submission, grader=student)
                submission_grade.status = StudentGradingStatus.DONE
                submission_grade.grade = request.grade
                submission_grade.save()
        else:
            raise BadRequestException(detail="Incorrect grade values")


def has_valid_grades_sum(submissions, n):
    # Calculate the expected sum of grades from 1 to N
    expected_sum = n * (n + 1) // 2
    # Get the sum of all grades in the submissions
    actual_sum = sum(submissions)

    # Compare the expected sum with the actual sum
    if actual_sum == expected_sum:
        return True
    else:
        return False
