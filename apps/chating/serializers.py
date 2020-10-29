from rest_framework.serializers import (
    Serializer,
    ModelSerializer, 
    PrimaryKeyRelatedField, RelatedField, ReadOnlyField, IntegerField,
    CharField, ImageField, DateField, DictField, SerializerMethodField,
    BooleanField, ModelField
)
from . import models
from . import fields
from apps.users_profile.serializers import ShortProfileSerializer
from apps.users_profile.models import Profile
from apps.chating.fields import DateTimeDictField
import datetime

class CreateChatMessageSerializer(ModelSerializer):
    id = IntegerField(required=False)
    profile_id = PrimaryKeyRelatedField(queryset=Profile.objects.all(), source='profile')
    chat_id = PrimaryKeyRelatedField(queryset=models.CommonChat.objects.all(), source='chat')
    last_modified = DateTimeDictField(default=datetime.datetime.now())
    is_modified = BooleanField(default=False)
    is_revised = BooleanField(default=False)
    is_deleted = BooleanField(default=False)

    class Meta:
        model = models.ChatMessage
        fields = (
            'id',
            'text',
            'profile_id',
            'chat_id',
            'last_modified',
            'is_modified',
            'is_revised',
            'is_deleted'
        )
    
    def create(self, validated_data):
        chat_message = models.ChatMessage.objects.create(**validated_data)
        id = chat_message.id
        return chat_message

class UpdateChatMessageSerializer(ModelSerializer):
    class Meta:
        model = models.ChatMessage
        fields = (
            'text',
        )
    def update(self, instance, validated_data):

        instance.text = validated_data.get('text', instance.text)
        instance.is_modified = True

        return instance

class ChatMessageSerializer(ModelSerializer):
    profile_id = PrimaryKeyRelatedField(queryset=Profile.objects.all(), source='profile')
    last_modified = fields.DateTimeDictField()
    class Meta:
        model = models.ChatMessage
        fields = (
            'id',
            'text',
            'last_modified',
            'is_modified',
            'is_revised',
            'is_deleted',
            'profile_id'
        )


class AbstractChatSerializer(ModelSerializer):

    def create_common_chat(self):
        common_chat: models.CommonChat = models.CommonChat.objects.create()
        common_chat.save()
        return common_chat

class CreateSavedMessagesChatSerializer(AbstractChatSerializer):
    profile_id = PrimaryKeyRelatedField(queryset=Profile.objects.all(), source='profile')

    class Meta:
        model = models.SavedMessagesChat
        fields = (
            'name', 
            'description',
            # 'common_chat',
            'profile_id'
        )

    def create(self, validated_data):

        validated_data['common_chat'] = super().create_common_chat()
        validated_data['image'] = 'assets/imageProfile_Kapkn3P.png'

        return models.SavedMessagesChat.objects.create(**validated_data)


class CreatePrivateChatSerializer(AbstractChatSerializer):
    profile_1_id = IntegerField(required=True)
    profile_2_id = IntegerField(required=True)


    class Meta:
        model = models.PrivateChat
        fields = (
            'profile_1_id', 
            'profile_2_id',
        )

    def create(self, validated_data):

        validated_data['common_chat'] = super().create_common_chat()

        return models.PrivateChat.objects.create(**validated_data)

# class CreateGroupChatSerializer(AbstractChatSerializer):
#     profiles = PrimaryKeyRelatedField(queryset=Profile.objects.all(), source='profile', many=True)


#     class Meta:
#         model = models.GroupChat
#         fields = (
#             'name',
#             'description',
#             'image',
#             'profiles',
#         )

#     def create(self, validated_data):

#         validated_data['common_chat'] = super().create_common_chat()

#         return models.GroupChat.objects.create(**validated_data)

class LastMessageSerializer(ModelSerializer):

    last_modified = fields.DateTimeDictField()

    class Meta:
        model = models.ChatMessage
        fields = (
            'id',
            'text',
            'profile_id',
            'last_modified',
        )
    
    # def get_created_at(self, obj):
    #     time_dict = {
    #         'year': obj.created_at.strftime('%Y'),
    #         'month': obj.created_at.strftime('%m'),
    #         'day': obj.created_at.strftime('%d'),
    #         'hour': obj.created_at.strftime('%H'),
    #         'minute': obj.created_at.strftime('%M'),
    #         'second': obj.created_at.strftime('%S'),
    #         'utc': obj.created_at.strftime('%z')
    #     }
    #     return time_dict

class ShortChatSerializer(Serializer):
    id = IntegerField()
    chat_type = CharField()
    name = CharField()
    image = ImageField()
    last_message = DictField(required=False)

class ShortSavedMessageChatSerializer(Serializer):
    id = IntegerField()
    chat_type = CharField()
    name = CharField()
    image = ImageField()
    last_message = DictField(required=False)

class ShortPrivateChatSerializer(Serializer):
    id = IntegerField()
    chat_type = CharField()
    profile = DictField(required=True)
    last_message = DictField(required=False)

class FullPrivateChatSerializer(Serializer):
    id = IntegerField()
    chat_type = CharField()
    profile = DictField(required=True) 

class FullChatSavedMessagesSerializer(Serializer):
    id = IntegerField()
    chat_type = CharField()
    name = CharField()
    image = ImageField() 
    # id = SerializerMethodField()
    # def get_id(self, chat_obj):
    #   return chat_obj.common_chat.id


    # class Meta:
    #     model = models.AbstractChat
    #     fields = (
    #         'id',
    #         'chat_type',
    #         'name',
    #         'image',
    #     )

       