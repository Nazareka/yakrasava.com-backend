from rest_framework.utils.serializer_helpers import ReturnDict
from apps.chating.models import PrivateChat, SavedMessagesChat
import datetime
from typing import Union, Tuple, List
from django.db.models.manager import BaseManager

from . import serializers
from apps.users_profile.models import Profile
from apps.users_profile.serializers import ShortProfileSerializer
from rest_framework.exceptions import ValidationError

def get_datetime_dict(datetime_obj: datetime.datetime):
    time_dict = {
        'year': datetime_obj.strftime('%Y'),
        'month': datetime_obj.strftime('%m'),
        'day': datetime_obj.strftime('%d'),
        'hour': datetime_obj.strftime('%H'),
        'minute': datetime_obj.strftime('%M'),
        'second': datetime_obj.strftime('%S'),
        'utc': datetime_obj.strftime('%z')
    }
    return time_dict

def get_serialized_chats(
    chat_querysets: Tuple[BaseManager[SavedMessagesChat], BaseManager[PrivateChat]], 
    current_profile_id: int
    ) -> List[ReturnDict]:

    chats: List[ReturnDict] = []
    chat_queryset = chat_querysets[0] # saved_messages_chats
    saved_messages_chats = []
    for chat_obj in chat_queryset:
        last_message_data = None
        try:
            last_message_obj = chat_obj.common_chat.messages.latest('created_at')
            last_message_sr = serializers.LastMessageSerializer(last_message_obj)
            last_message_data = last_message_sr.data
        except:
            pass
        chat = {
            'id': chat_obj.common_chat.id,
            'chat_type': chat_obj.chat_type,
            'name': chat_obj.name,
            'image': chat_obj.image,
            'last_message': last_message_data
        }
        saved_messages_chats.append(chat)
    saved_messages_chats_sr = serializers.ShortSavedMessageChatSerializer(
        data=saved_messages_chats, 
        many=True
    )
    saved_messages_chats_sr.is_valid()
    chats.extend(saved_messages_chats_sr.data)
    
    chat_queryset = chat_querysets[1] # private_chats
    private_chats = []
    for chat_obj in chat_queryset:
        last_message_data = None
        try:
            last_message_obj = chat_obj.common_chat.messages.latest('created_at')
            last_message_sr = serializers.LastMessageSerializer(last_message_obj)
            last_message_data = last_message_sr.data
        except:
            pass
        profile_1_id = chat_obj.profile_1.id
        profile_2_id = chat_obj.profile_2.id
        profile_data = None
        if (profile_1_id != current_profile_id):
            another_profile = Profile.objects.get(id=profile_1_id)
            another_profile_sr = ShortProfileSerializer(another_profile)
            profile_data = another_profile_sr.data
        else:
            another_profile = Profile.objects.get(id=profile_2_id)
            another_profile_sr = ShortProfileSerializer(another_profile)
            profile_data = another_profile_sr.data
        
        chat = {
            'id': chat_obj.common_chat.id,
            'chat_type': chat_obj.chat_type,
            'profile': profile_data,
            'last_message': last_message_data
        }
        private_chats.append(chat)
    private_chats_sr = serializers.ShortPrivateChatSerializer(
        data=private_chats, 
        many=True
    )
    private_chats_sr.is_valid()
    chats.extend(private_chats_sr.data)
    return chats

def get_serialized_chat(
    chat_obj: Union[SavedMessagesChat, PrivateChat], 
    current_profile_id: int, 
    common_chat_id: int
    ) -> ReturnDict:

    chat = {}
    if isinstance(chat_obj, SavedMessagesChat):
        chat = {
            'id': common_chat_id,
            'chat_type': chat_obj.chat_type,
            'name': chat_obj.name,
            'image': chat_obj.image
        }
        chat_sr = serializers.FullChatSavedMessagesSerializer(data=chat)
        if not chat_sr.is_valid():
            raise ValidationError(str(chat_sr.errors), code='invalid')

    else:
        profile_1_id = chat_obj.profile_2.id
        profile_2_id = chat_obj.profile_2.id

        if (profile_1_id != current_profile_id):
            another_profile: Profile = Profile.objects.get(id=profile_1_id)
        else:
            another_profile: Profile = Profile.objects.get(id=profile_2_id)
        
        profile_data = ShortProfileSerializer(another_profile).data
        chat = {
            'id': common_chat_id,
            'chat_type': chat_obj.chat_type,
            'profile': profile_data
        }
        chat_sr = serializers.FullPrivateChatSerializer(data=chat)
        if not chat_sr.is_valid():
            raise ValidationError(str(chat_sr.errors), code='invalid')

    return chat_sr.data