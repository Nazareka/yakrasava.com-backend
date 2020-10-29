from django.db.models import Q
from django.db.models.manager import BaseManager

from rest_framework.decorators import action
from rest_framework.views import APIView 
from rest_framework.viewsets import ViewSetMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_302_FOUND
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request

from apps.users_profile.models import Profile

from typing import Tuple

from . import models
from . import serializers
from . import utils

# import datetime

# datetime.datetime.__dict__

class ChatViewSet(ViewSetMixin, APIView):

    permission_classes = [IsAuthenticated,]
    # current_profile_id: Union[int, None] = None

    def get_permissions(self):
        return [permission() for permission in self.permission_classes]

    @action(detail=False, methods=['POST'])
    def create_saved_messages_chat(self, request: Request) -> Response:

        current_profile_id: int = request.user.profile.id
        
        if models.SavedMessagesChat.objects \
            .filter(profile_id=current_profile_id) \
            .only('id') \
            .exists():
            return Response({"message":'SavedMessagesChat already exists'}, status=HTTP_302_FOUND)
        else:
            Saved_messages_ser = serializers.CreateSavedMessagesChatSerializer(
                data={
                    'name': "Saved Messages",
                    'description': "there are your Saved Messages",
                    'profile_id': current_profile_id,
                }
            )
            Saved_messages_ser.is_valid()
            Saved_messages_obj = Saved_messages_ser.save()
            Saved_messages_message_object = serializers.CreateChatMessageSerializer(
                data={
                    'text': 'You are welcome in Saved messages! You can write anything you need!',
                    'profile_id': current_profile_id,
                    'chat_id': Saved_messages_obj.common_chat.id
                }
            )
            Saved_messages_message_object.is_valid()
            Saved_messages_message_object.save()

            return Response({"message":'Saved messages chat was successfully added!'}, status=HTTP_200_OK)

    @action(detail=False, methods=['POST'])
    def create_private_chat(self, request: Request) -> Response:
        current_profile_id: int = request.user.profile.id
        if (profile_id := request.data.get('profile_id')):
            another_profile_id: int = profile_id
            try:
                private_chat_obj = models.PrivateChat.objects.only('id').get(
                    Q(profile_1_id=current_profile_id, profile_2_id=another_profile_id) 
                    |
                    Q(profile_1_id=another_profile_id, profile_2_id=current_profile_id)
                )
                json = JSONRenderer().render(private_chat_obj.common_chat.id)
                return Response({"message":json}, status=HTTP_200_OK)

            except models.PrivateChat.DoesNotExist:
                private_chat_sr = serializers.CreatePrivateChatSerializer(
                    data = {
                        "profile_1_id": current_profile_id,
                        "profile_2_id": another_profile_id
                    }
                )
                private_chat_sr.is_valid()
                private_chat_obj = private_chat_sr.save()
                json = JSONRenderer().render(private_chat_obj.common_chat.id)
                return Response({"message":json}, status=HTTP_200_OK)
        else:
            return Response({"message":'profile id is None!'}, status=HTTP_404_NOT_FOUND)

    # in feature
    
    # @action(detail=False, methods=['POST'])
    # def create_group_chat(self, request) -> Response:

    #     current_profile_id: int = request.user.profile.id
    #     name = request.data.get('name')
    #     description = request.data.get('description')
    #     image = request.data.get('image')

    #     group_chat_sr = serializers.CreateGroupChatSerializer(
    #         data = {
    #             'name': name,
    #             'description': description,
    #             'image': image
    #         }
    #     )
    #     group_chat_sr.is_valid()
    #     group_chat_sr.save()

    #     return Response({"message":'GroupChat chat was successfully added!'}, status=HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def get_all_chats(self, request: Request) -> Response:

        current_profile_id: int = request.user.profile.id

        saved_messages_chats = models.SavedMessagesChat.objects.filter(profile_id=current_profile_id)

        private_chats = models.PrivateChat.objects.filter(
            Q(profile_1_id=current_profile_id) |
            Q(profile_2_id=current_profile_id)
        )

        chat_querysets = (
            saved_messages_chats, 
            private_chats
        )
        chats = utils.get_serialized_chats(chat_querysets, current_profile_id)
        
        json = JSONRenderer().render(chats)

        return Response({"message":json}, status=HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def get_chat_by_id(self, request: Request) -> Response:

        current_profile_id: int = request.user.profile.id
        if (chat_id := request.GET.get('chat_id')):
            common_chat_id: int = int(chat_id)
            common_chat_obj = models.CommonChat.objects.get(id=common_chat_id)
            chat_obj = common_chat_obj.special_chat
            
            chat = utils.get_serialized_chat(chat_obj, current_profile_id, common_chat_id)

            json = JSONRenderer().render(chat)

            return Response({"message":json}, status=HTTP_200_OK)
        else:
            return Response({"message":'chat_id is None!'}, status=HTTP_404_NOT_FOUND)


class ChatMessageViewSet(ViewSetMixin, APIView):

    permission_classes = [IsAuthenticated,]
    
    def get_permissions(self):
        return [permission() for permission in self.permission_classes]
    
    @action(detail=False, methods=['GET'])
    def get_messages_by_chat_id(self, request: Request) -> Response:

        if (chat_id := request.GET.get('chat_id')):
            common_chat_id: int = int(chat_id)

            common_chat_obj: models.CommonChat = models.CommonChat.objects.get(id=common_chat_id)
            messages_qs = common_chat_obj.messages.all()
            messages_sr = serializers.ChatMessageSerializer(messages_qs, many=True)
            json = JSONRenderer().render(messages_sr.data)

            return Response({"message":json}, status=HTTP_200_OK)
        else:
            return Response({"message":'chat_id is None!'}, status=HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['POST'])
    def create_message(self, request: Request) -> Response:

        current_profile_id: int = request.user.profile.id

        if ((text_data := request.data.get('text') )and (chat_id := request.data.get('chat_id'))):
            text: str = text_data
            common_chat_id: int = int(chat_id)

            chat_message_sr = serializers.CreateChatMessageSerializer(data={
                'text': text,
                'profile_id': current_profile_id,
                'chat_id': common_chat_id
            })
            chat_message_sr.is_valid()
            print(chat_message_sr)
            chat_message_sr.save()

            return Response({"message":'Message was created!'}, status=HTTP_200_OK)
        else:
            return Response({"message":'text or chat_id is None!'}, status=HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['POST'])
    def update_message(self, request) -> Response:

        chat_message_id: int = int(request.data.get('chat_message_id'))
        new_text: str = request.data.get('new_text')

        chat_message_obj: models.ChatMessage = models.ChatMessage.objects.get(id=chat_message_id)

        chat_message_sr = serializers.UpdateChatMessageSerializer(chat_message_obj, data={
            'text': new_text,
        })
        chat_message_sr.is_valid()
        chat_message_sr.save()
        json = JSONRenderer().render(chat_message_sr.data)

        return Response({"message":'Message was updated!'}, status=HTTP_200_OK)
        
