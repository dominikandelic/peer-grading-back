from django.contrib import admin

from .models import User, Student, Teacher, Course, Task, Submission, Grading, SubmissionGrade, GradingResult

admin.site.register(User)
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Course)
admin.site.register(Task)
admin.site.register(Submission)
admin.site.register(Grading)
admin.site.register(SubmissionGrade)
admin.site.register(GradingResult)