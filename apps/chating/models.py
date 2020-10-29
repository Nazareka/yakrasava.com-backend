from apps.users_profile.models import Profile
from django.core.checks.messages import Error
from django.db import models
from django.db.models import *
from typedmodels.models import TypedModel
from typing import Any, Union
import datetime
from django.db.models.manager import BaseManager
class AbstractChat(Model):
    created_at = DateField(auto_now_add=True)
    common_chat = OneToOneField(
        'CommonChat',
        on_delete=CASCADE,
        null=True
    )

    @property
    def messages(self) -> BaseManager['ChatMessage']:
        messages_qs = self.common_chat.messages

        return messages_qs

    class Meta:
        abstract = True

class CommonChat(Model):

    @property
    def special_chat(self) -> Union['SavedMessagesChat', 'PrivateChat']:
        special_chats = (
            'privatechat',
            'savedmessageschat'
        )
        for special_chat in special_chats:
            if hasattr(self, special_chat):
                return getattr(self, special_chat) 
        
        raise NotImplementedError()

class SavedMessagesChat(AbstractChat):
    chat_type = 'saved_messages_chat'

    name = CharField(max_length=50, blank=False)
    description = CharField(max_length=256, default='')
    image = ImageField(upload_to='assets', max_length=None, default='')

    profile = OneToOneField(
        'users_profile.Profile',
        on_delete=CASCADE,
        related_name='profile',
        null=True
    )

class PrivateChat(AbstractChat):
    chat_type = 'private_chat'

    profile_1 = ForeignKey(
        'users_profile.Profile',
        related_name='profile_1', 
        on_delete=CASCADE,
        null=True
    )
    profile_2 = ForeignKey(
        'users_profile.Profile',
        related_name='profile_2',
        on_delete=CASCADE,
        null=True
    )

# class GroupChat(AbstractChat):
#     chat_type = 'group_chat'
#     members = ManyToManyField(
#         'users_profile.Profile',
#         related_name='members'
#     )


class ChatMessage(Model):
    text = CharField(max_length=1000)
    created_at = DateTimeField(auto_now_add=True)
    last_modified = DateTimeField(auto_now=True)
    is_modified = BooleanField(default=False)
    is_revised = BooleanField(default=False)
    is_deleted = BooleanField(default=False)

    profile = ForeignKey(
        'users_profile.Profile',
        on_delete=CASCADE,
        null=True
    )
    chat = ForeignKey(
        'CommonChat',
        on_delete=CASCADE,
        related_name='messages',
        null=True
    )
    class Meta: 
        ordering = ['created_at',]



