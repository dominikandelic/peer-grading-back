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


class Task(models.Model):
    name = models.CharField(max_length=255)
    file = models.CharField(max_length=255)
    submissions = models.ManyToManyField("Submission")


class Submission(models.Model):
    file = models.CharField(max_length=255)
    submission_task = models.ForeignKey(Task, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)


class Grading(models.Model):
    class GradingStatus(models.TextChoices):
        STARTED = "STARTED"
        STANDBY = "STANDBY"
        FINISHED = "FINISHED"

    task = models.OneToOneField(Task, on_delete=models.CASCADE)
    instructions = models.TextField()
    submissions_number = models.IntegerField(validators=[MinValueValidator(1)])
    deadline = models.DateTimeField()
    status = models.CharField(
        choices=GradingStatus.choices, default=GradingStatus.STANDBY, max_length=15
    )


class SubmissionGrade(models.Model):
    grader = models.ForeignKey(Student, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    grade = models.IntegerField()
