from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async, async_to_sync
from apps.users_profile.models import Profile
from apps.relationship.models import Relationship
# from chat.models import Message
import json
from apps.chating.serializers import CreateChatMessageSerializer
from rest_framework.renderers import JSONRenderer

class UserConsumer(AsyncWebsocketConsumer):
    profile_id: int
    profile_object: Profile
    profile_group: str # example "profile_132132"
    watching_profile_status_group: str # example "profile_watching_status_132132"

    async def connect(self):
        user_id = self.scope["user_id"]
        response = self.scope["response"]

        if user_id is None and response == 'InvalidToken':
            await self.accept()
            await super().close(code=4003)
        else:
            await self.accept()
            try:
                self.profile_object = await database_sync_to_async(Profile.objects.get)(user_id=user_id)
                self.profile_id = self.profile_object.id

                self.watching_profile_status_group = 'watching_profile_status_' + str(self.profile_id)

                await self.channel_layer.group_send(
                    self.watching_profile_status_group,
                    {
                        "type": "profile_status_changes",
                        "message": {
                            "profile": self.profile_id,
                            "status": "online"
                        }
                    }
                )

                self.profile_object.status = 1
                await database_sync_to_async(self.profile_object.save)()

            except Exception as e:
                print(e)
                await super().close(code=4004)

    async def disconnect(self, close_code):
        print(close_code, 'close_code')
        if (close_code != 4004 and close_code != 4003):

            await self.channel_layer.group_send(
                self.watching_profile_status_group,
                {
                    "type": "profile_status_changes",
                    "message": {
                        "profile": self.profile_id,
                        "status": "offline"
                    }
                }
            )
            self.profile_object.status = 0
            await database_sync_to_async(self.profile_object.save)()
            print("user was disconnected")

    async def receive(self, text_data):
        # Receive message from WebSocket
        print("receive")
        json_data = json.loads(text_data)
        if (json_data["command"] == 'sub_to_chat'):
            await self.sub_to_chat(json_data)
        elif (json_data["command"] == 'unsub_to_chat'):
            await self.unsub_to_chat(json_data)
        elif (json_data["command"] == 'sub_to_profile_status'):
            await self.sub_to_profile_status(json_data)
        elif (json_data["command"] == 'unsub_to_profile_status'):
            await self.unsub_to_profile_status(json_data)
        elif (json_data["command"] == 'send_message'):
            await self.send_message(json_data)

    async def watching_for_another_profile_status(self, data):
        another_profile_id = data["message"]
        another_watching_status_group = 'profile_watching_status_' + str(another_profile_id)
        await self.channel_layer.group_add(
            another_watching_status_group,
            self.channel_name
        )
    async def profile_status_changes(self, event):
        await self.send(text_data=json.dumps(event))
    
    async def sub_to_chat(self, data):
        chat_id = data["message"]
        print('watching' + str(chat_id) )
        watching_chat_group = 'watching_chat' + str(chat_id)
        await self.channel_layer.group_add(
            watching_chat_group,
            self.channel_name
        )

    async def unsub_to_chat(self, data):
        chat_id = data["message"]
        print('unsub_to_chat' + str(chat_id) )
        watching_chat_group = 'watching_chat' + str(chat_id)
        await self.channel_layer.group_discard(
            watching_chat_group,
            self.channel_name
        )
    
    async def sub_to_profile_status(self, data):
        profile_id = data["message"]
        print('sub_to_profile_status' + str(profile_id) )
        watching_profile_status_group = 'watching_profile_status_' + str(profile_id)
        await self.channel_layer.group_add(
            watching_profile_status_group,
            self.channel_name
        )

    async def unsub_to_profile_status(self, data):
        profile_id = data["message"]
        print('unsub_to_profile_status' + str(profile_id) )
        watching_profile_status_group = 'watching_profile_status_' + str(profile_id)
        await self.channel_layer.group_discard(
            watching_profile_status_group,
            self.channel_name
        )
    
    async def send_message(self, event):
        text = event["message"]['text']
        common_chat_id = event["message"]['chat_id']

        chat_message_sr = await sync_to_async(CreateChatMessageSerializer)(data={
            'text': text,
            'profile_id': self.profile_id,
            'chat_id': common_chat_id
        })
        await sync_to_async(chat_message_sr.is_valid)()
        await sync_to_async(chat_message_sr.save)()
        watching_chat_group = 'watching_chat' + str(common_chat_id)
        await self.channel_layer.group_send(
            watching_chat_group,
            {
                "type": "new_message",
                "message": {
                    "chat_message": chat_message_sr.data
                }
            }
        )
    
    async def new_message(self, event):
        await self.send(text_data=json.dumps(event))