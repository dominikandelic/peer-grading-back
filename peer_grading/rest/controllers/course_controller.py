from typing import List

from ninja_jwt.authentication import JWTAuth
from ninja_extra import api_controller, route

from peer_grading.models import Student, Course, Teacher
from peer_grading.rest.controllers.task_controller import order_tasks_by_deadline
from peer_grading.rest.exceptions.exceptions import BadRequestException
from peer_grading.rest.schemas.schemas_in import EnrollStudentRequest, CreateCourseRequest, UpdateCourseRequest
from peer_grading.rest.schemas.schemas_out import UserResponse, CourseResponse, TaskResponse


@api_controller(auth=JWTAuth(), tags=["Course"])
class CourseController:
    @route.get("/courses", response=List[CourseResponse])
    def get_courses(self):
        courses = Course.objects.get_queryset()
        return list(courses)

    @route.get("/courses/{course_id}", response=CourseResponse)
    def get_course(self, course_id: int):
        return Course.objects.get(pk=course_id)

    @route.get(
        "/teachers/{teacher_id}/courses/",
        response=List[CourseResponse]
    )
    def get_teacher_courses(self, teacher_id):
        teacher = Teacher.objects.get(pk=teacher_id)
        return list(teacher.course_set.all())

    @route.get(
        "/students/{student_id}/courses/",
        response=List[CourseResponse],

    )
    def get_student_courses(self, student_id):
        student = Student.objects.get(pk=student_id)
        return list(student.course_set.all())

    @route.get("/courses/{course_id}/tasks/", response=List[TaskResponse])
    def get_course_tasks(self, course_id: int):
        course = Course.objects.get(pk=course_id)
        return order_tasks_by_deadline(course.task_set.all())

    @route.get("/courses/{course_id}/students/", response=List[UserResponse])
    def get_enrolled_students(self, course_id: int):
        course = Course.objects.get(pk=course_id)
        return course.students.all()

    @route.post("/courses", response={200: str})
    def create_course(self, payload: CreateCourseRequest):
        if self.context.request.auth.is_superuser or self.context.request.auth.is_teacher:
            try:
                teacher = Teacher.objects.get(pk=payload.teacher_id)
                Course.objects.create(name=payload.name, teacher=teacher)
            except:
                raise BadRequestException(detail="Došlo je do pogreške", code="CREATE_ERROR")
            return "OK"
        raise BadRequestException(detail="Došlo je do pogreške", code="CREATE_ERROR")

    @route.put(
        "/courses/{course_id}/enroll-students",
        response={200: str},
    )
    def enroll_student(self, payload: EnrollStudentRequest, course_id: int):
        if self.context.request.auth.is_superuser or self.context.request.auth.is_teacher:
            try:
                student = Student.objects.get(pk=payload.student_id)
                course = Course.objects.get(pk=course_id)
                course.students.add(student)
                course.save()
            except:
                raise BadRequestException(detail="Došlo je do pogreške", code="ALREADY_ENROLLED")
            return "OK"
        raise BadRequestException(detail="Došlo je do pogreške", code="CREATE_ERROR")

    @route.put("/courses/{course_id}", response={200: str})
    def update_course(self, payload: UpdateCourseRequest, course_id: int):
        try:
            course = Course.objects.get(pk=course_id)
            if course.teacher.id == self.context.request.auth.id or self.context.request.auth.is_superuser:
                course.name = payload.name
                course.save()
        except:
            raise BadRequestException(detail="Došlo je do pogreške", code="UPDATE_ERROR")
        return "OK"

    @route.delete("/courses/{course_id}")
    def delete_course(self, course_id: int):
        try:
            course = Course.objects.get(pk=course_id)
            if course.teacher.id == self.context.request.auth.id or self.context.request.auth.is_superuser:
                course.delete()
        except:
            raise BadRequestException(detail="Došlo je do pogreške", code="DELETE_ERROR")
