from ninja_extra import api_controller, route
from ninja_jwt.controller import TokenObtainPairController

from peer_grading.rest.schemas.schemas_out import MyTokenObtainPairOutSchema, MyTokenObtainPairSchema


@api_controller("/token", tags=["Auth"])
class MyTokenObtainPairController(TokenObtainPairController):
    @route.post(
        "/pair", response=MyTokenObtainPairOutSchema, url_name="token_obtain_pair"
    )
    def obtain_token(self, user_token: MyTokenObtainPairSchema):
        return user_token.output_schema()
