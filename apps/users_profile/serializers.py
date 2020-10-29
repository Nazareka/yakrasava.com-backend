from rest_framework.serializers import (
    Serializer, ModelSerializer, CharField, ChoiceField, DictField, SerializerMethodField,
    IntegerField, ImageField, 
)
from rest_framework.settings import api_settings

from . import models

relates = (
    'none', 
    'from', 
    'to'
)
statusesRS = (
    'none',
    'follow',
    'friend',
    'close_friend',
    'relative',
    'beloved'
)
statuses = (
    'offline',
    'online'
)
sex_choices = (
    ('ML', 'Male'),
    ('FM', 'Female'),
    ('OT', 'other'),
)

class UserSerializerWithToken(ModelSerializer):
    password = CharField(write_only=True)
    token = SerializerMethodField()
    def get_token(self, object):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(object)
        token = jwt_encode_handler(payload)
        return token
    def create(self, validated_data):
        user = models.User.objects.create(
            email = validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    class Meta:
        model = models.User
        fields = ('password', 'token', 'email')


class CreateProfileSerializer(ModelSerializer):
    user_id = IntegerField()
    image = ImageField()

    def create(self, validated_data):
        profile = models.Profile.objects.create(
            user_id = validated_data['user_id'],
            location = validated_data['location'],
            sex = validated_data['sex'],
            date_of_birth = validated_data['date_of_birth'],
            image = validated_data['image'],
        )
        return profile

    class Meta:
        model = models.Profile
        fields = ('user_id',' location', 'sex', 'date_of_birth', 'image')

class ShortProfileSerializer(ModelSerializer):
    status = CharField(source='get_status_display')
    
    class Meta:
        model = models.Profile
        fields = ('id', 'nickname', 'image', 'status')

class ShortProfileWithRelateStatusSerializer(Serializer):
    profile = ShortProfileSerializer()
    related = ChoiceField(relates)
    status = ChoiceField(statusesRS)

class FullProfileSerializer(ModelSerializer):
    status = CharField(source='get_status_display')
    class Meta:
        model = models.Profile
        fields = (
            'id', 
            'nickname', 
            'main_quote', 
            'profession', 
            'location', 
            'sex', 
            'date_of_birth', 
            'image', 
            'status'
        )

class FullProfileWithRelateStatusSerializer(Serializer):
    profile = DictField()
    related = ChoiceField(relates)
    status = ChoiceField(statusesRS)
