import json
import time
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Monitor_operation
from .cursor_cache import get_active_cursor

class DrawingConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time drawing updates.
    Broadcasts when cursor moves to a different operation.
    """

    async def connect(self):
        # Join the drawing broadcast group
        self.group_name = 'drawing_updates'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        # Send initial drawing if cursor is active
        cursor_data = get_active_cursor()
        if cursor_data and cursor_data['is_active']:
            drawing_data = await self.get_drawing_data(cursor_data['operation_id'])
            await self.send(text_data=json.dumps(drawing_data))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Not expecting client to send data, but handle if needed
        pass

    # Receive message from group broadcast
    async def drawing_update(self, event):
        """
        Called when a drawing_update message is broadcast to the group.
        Only sends operation_id - client looks up image from preloaded cache.
        """
        await self.send(text_data=json.dumps({
            'type': 'drawing',
            'operation_id': event['operation_id'],
            'operation_name': event['operation_name'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def get_drawing_data(self, operation_id):
        """Fetch drawing data from database (without image - cached on client)."""
        try:
            operation = Monitor_operation.objects.get(pk=operation_id)
            return {
                'type': 'drawing',
                'operation_id': operation.id,
                'operation_name': operation.name,
                'timestamp': int(time.time())
            }
        except Monitor_operation.DoesNotExist:
            return {
                'type': 'error',
                'message': 'Operation not found'
            }
