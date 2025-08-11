import json
from channels.generic.websocket import AsyncWebsocketConsumer

class LiveLogConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("logs", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("logs", self.channel_name)

    async def log_message(self, event):
        await self.send(text_data=json.dumps(event["event"]))
