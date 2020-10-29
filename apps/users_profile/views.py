from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.views import APIView 
from rest_framework.viewsets import ViewSetMixin
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST
from rest_framework.exceptions import ValidationError

from typing import Union, Tuple, List, Optional
from typing_extensions import TypedDict

from apps.relationship.utils import (
    get_list_relationships_friends_by_profile_id,
    get_list_relationships_followers_by_profile_id,
    get_list_relationships_follows_by_profile_id,
)

from . import models
from . import serializers
from . import utils

class TUser(TypedDict):
    nickname: str
    email: str
    password: str

class ProfileViewSet(ViewSetMixin, APIView):

    permission_classes: List

    def get_permissions(self):
        if self.action in (
            'create_user',
            'get_full_profile_current_user',
            'get_full_profile_by_profile_id_authed',
            'get_list_friends_current_user',
            'get_list_followers_current_user',
            'get_list_follows_current_user',
        ):
            self.permission_classes = [IsAuthenticated,]
        elif self.action in (
            'get_full_profile_by_profile_id_unauthed',
            'get_list_users_by_query_string',
            'get_list_users_by_array_ids',
        ):
            self.permission_classes = [AllowAny,]
        return [permission() for permission in self.permission_classes]

    @action(detail=False, methods=['POST'])
    def create_user(self, request: Request) -> Response:
        if (user_data := request.data.get('user')):
            user: TUser = user_data
            serializer = serializers.UserSerializerWithToken(data=user)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "User created succesfully"}, status=HTTP_200_OK) 
            else:
                return Response({"message": "data is invalid"}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "data is None"}, status=HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['GET'])
    def get_profile_id_by_current_user(self, request: Request) -> Response:
        profile_id: Optional[int] = None
        try:
            profile: models.Profile = request.user.profile
            profile_id = profile.id
        except:
            pass
        data = {
            "user": {
                "profile_id": profile_id
            }
        }
        return Response({"message": data}, status=HTTP_200_OK)

    @action(detail=False, methods=['POST'])
    def create_profile(self, request: Request) -> Response:
        if (profile_data := request.data):
            serializer = serializers.CreateProfileSerializer(data=profile_data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "profile was successfuly created"}, status=HTTP_200_OK) 
            else:
                return Response({"message": 'data is invalid'}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": 'data is None'}, status=HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['GET'])
    def get_full_profile_current_user(self, request: Request) -> Response:
        """
            get full explained profile of current logged user
            
        """

        profile_object = request.user.profile
        serializer = serializers.FullProfileSerializer(profile_object)

        json = JSONRenderer().render(serializer.data)
        return Response(json, status=HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def get_full_profile_by_profile_id_authed(self, request: Request) -> Response:
        """
            get full explained profile with rs status of current logged user
            
        """
        current_profile_id: int = request.user.profile.id
        another_profile_id = request.GET.get('profile_id')

        try:
            another_profile_object = models.Profile.objects.get(id=another_profile_id)
        except models.Profile.DoesNotExist:
            return Response(
                "Another user's profile doesn't exist", 
                status=HTTP_404_NOT_FOUND
            )

        profile_with_status = utils.get_full_profile_with_rs_status_another_user(
            current_profile_id, 
            another_profile_object.id, 
            another_profile_object
        )
        serializer = serializers.FullProfileWithRelateStatusSerializer(data=profile_with_status)

        if not serializer.is_valid():
            raise ValidationError(str(serializer.errors), code='invalid')

        json = JSONRenderer().render(serializer.data)

        return Response(json, status=HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def get_list_friends_current_user(self, request: Request) -> Response:
        current_profile_id: int = request.user.profile.id
        list_rs_friend = get_list_relationships_friends_by_profile_id(current_profile_id)
        list_friends = utils.get_list_related_users(list_rs_friend, "from")

        serializer = serializers.ShortProfileSerializer(list_friends, many=True)

        json = JSONRenderer().render(serializer.data)
        return Response(json)

    @action(detail=False, methods=['GET'])
    def get_list_followers_current_user(self, request: Request) -> Response:

        current_profile_id: int = request.user.profile.id
        list_rs_followers = get_list_relationships_followers_by_profile_id(current_profile_id)
        list_followers = utils.get_list_related_users(list_rs_followers, "from")

        serializer = serializers.ShortProfileSerializer(list_followers, many=True)

        json = JSONRenderer().render(serializer.data)
        return Response(json)

    @action(detail=False, methods=['GET'])
    def get_list_follows_current_user(self, request: Request) -> Response:

        current_profile_id: int = request.user.profile.id
        list_rs_follows = get_list_relationships_follows_by_profile_id(current_profile_id)
        list_follows = utils.get_list_related_users(list_rs_follows, "to")

        serializer = serializers.ShortProfileSerializer(list_follows, many=True)

        json = JSONRenderer().render(serializer.data)
        return Response(json)

    @action(detail=False, methods=['GET'])
    def get_list_users_by_query_string(self, request: Request) -> Response:
        current_profile_id: int = request.user.profile.id
        query_string = request.GET.get('query_string')

        list_profiles = models.Profile.objects.filter(nickname__icontains=query_string)
        print(list_profiles)
        if list_profiles.exists():
            serializer = serializers.ShortProfileSerializer(list_profiles, many=True)
            json = JSONRenderer().render(serializer.data)
            return Response(json)
        else:
            json = JSONRenderer().render('none')
            return Response(json)

    @action(detail=False, methods=['GET'])
    def get_list_users_by_array_ids(self, request: Request) -> Response:

        array_ids = request.GET.getlist('array_ids[]')
        current_profile_id: int = request.user.profile.id
        list_profiles = models.Profile.objects.filter(id__in=array_ids)
        if list_profiles.exists():
            serializer = serializers.ShortProfileSerializer(list_profiles, many=True)
            json = JSONRenderer().render(list_profiles)
            return Response(json)
        else:
            json = JSONRenderer().render('none')
            return Response(json)



        


