from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST
from rest_framework.request import Request

from typing import Tuple, Union

from .models import Relationship
from apps.users_profile.models import Profile
from . import models
from . import types
from . import utils

class ChangeRelationshipView(APIView):
    permission_classes = (IsAuthenticated, )
    
    actions: types.TTupleRsActions = ('follow', 'unfollow', 'make_friend', 'unfriend', 'make_close_friend', 'make_relative', 'make_beloved',
                    'unmake_close_friend', 'unmake_relative', 'unmake_beloved')

    def post(self, request: Request) -> Response:
        current_profile_id: int = request.user.profile.id
        if (profile_id := request.data.get('profile_id')):
            another_profile_id: int = profile_id

            if not Profile.objects.filter(id=another_profile_id).exists():
                return Response({"message": "Friend's profile doesn't exist"}, status=HTTP_404_NOT_FOUND)

            action: types.TUnionRsActions = request.data["action"]

            if not(action in self.actions):
                return Response({"message": "invalid action"}, status=HTTP_400_BAD_REQUEST)

            if action == 'follow':
                utils.follow_user(current_profile_id, another_profile_id)
            elif action == 'unfollow':
                utils.unfollow_user(current_profile_id, another_profile_id)
            elif action == 'make_friend':
                utils.make_user_friend(current_profile_id, another_profile_id)
            elif action == 'unfriend':
                utils.unfriend_user(current_profile_id, another_profile_id)
            elif action == 'make_close_friend':
                utils.make_user_close_friend(current_profile_id, another_profile_id)
            elif action == 'make_relative':
                utils.make_user_relative(current_profile_id, another_profile_id)
            elif action == 'make_beloved':
                utils.make_user_beloved(current_profile_id, another_profile_id)
            elif action == 'unmake_close_friend' or action == 'unmake_relative' or action == 'unmake_beloved':
                utils.unmake_user_special_friend(current_profile_id, another_profile_id)

            return Response(status=HTTP_200_OK)
        else:
            return Response({"message": 'profile id is None!'}, status=HTTP_404_NOT_FOUND)
