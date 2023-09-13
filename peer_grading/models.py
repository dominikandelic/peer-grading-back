from django.db import models
from django.contrib.auth.models import AbstractUser

from django.core.validators import MinValueValidator


class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Teacher(User):
    pass


class Student(User):
    pass


class Course(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    students = models.ManyToManyField(Student)

    def __str__(self):
        return self.name


class Task(models.Model):
    name = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField()

    def __str__(self):
        return self.name


class Submission(models.Model):
    file = models.FileField(upload_to="submissions/")
    submission_task = models.ForeignKey(Task, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.student.first_name + " " + self.student.last_name \
            + "'s submission for task " + self.submission_task.name


class GradingStatus(models.TextChoices):
    STARTED = "STARTED"
    STANDBY = "STANDBY"
    FINISHED = "FINISHED"


class Grading(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name="grading")
    instructions = models.TextField()
    submissions_number = models.IntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        choices=GradingStatus.choices, default=GradingStatus.STANDBY, max_length=15
    )

    def __str__(self):
        return self.task.name


class StudentGradingStatus(models.TextChoices):
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class SubmissionGrade(models.Model):
    grader = models.ForeignKey(Student, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    grade = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        choices=StudentGradingStatus.choices, default=StudentGradingStatus.IN_PROGRESS, max_length=15
    )

    def __str__(self):
        return self.grader.first_name + " " + self.grader.last_name \
            + "'s grade of " + self.submission.student.first_name + " " + self.submission.student.last_name \
            + "'s submission for task " + self.submission.submission_task.name


class GradingResult(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    total_score = models.IntegerField()
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.submission.submission_task.name
