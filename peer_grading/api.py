from ninja_extra import NinjaExtraAPI

from peer_grading.rest.controllers.course_controller import CourseController
from peer_grading.rest.controllers.grading_controller import GradingController
from peer_grading.rest.controllers.submission_controller import SubmissionController
from peer_grading.rest.controllers.task_controller import TaskController
from peer_grading.rest.controllers.token_controller import MyTokenObtainPairController
from peer_grading.rest.controllers.user_controller import UserController
from peer_grading.rest.utils.renderers import ORJSONRenderer

api = NinjaExtraAPI(renderer=ORJSONRenderer())
api.register_controllers(MyTokenObtainPairController,
                         CourseController,
                         SubmissionController,
                         TaskController,
                         UserController,
                         GradingController)