from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from .chatgui import bot_reply
from .models import *
import pickle
from django.db.models import Q
from googletrans import Translator


class Notify(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['secret_key']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        talk_type = text_data_json['talk_type']
        last_quest = text_data_json['last_ques']
        secret_key = text_data_json['secret_key']
        user_id = text_data_json['user_id']
        company = Company.objects.get(secret_key=secret_key)
        customer = Customer.objects.get(u_field=user_id)
        talk = 'note_no' if talk_type == 'notification_no' else 'note_yes'
        note = Notification.objects.create(company=company, customer=customer, message=last_quest,
                                            note_type=talk)
        note_number, created = NotifyNumber.objects.get_or_create(
                                                    company=company,
                                                    note_type=talk,
                                                    defaults={'number': 1}
                                                    )
        if not created:
            note_number.number += 1
            note_number.save()
        note_id = note.pk
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'talk_type': talk_type,
                'last_quest': last_quest,
                'secret_key': secret_key,
                'user_id': user_id,
                'note_id': note_id,

            }
        )

    # Receive message from room group
    def chat_message(self, event):
        talk_type = event['talk_type']
        last_quest = event['last_quest']
        secret_key = event['secret_key']
        user_id = event['user_id']
        note_id = event['note_id']

        self.send(text_data=json.dumps({
            'talk_type': talk_type,
            'last_quest': last_quest,
            'secret_key': secret_key,
            'user_id': user_id,
            'note_id': note_id,
        }))


class ChatToCustomerConsumer(WebsocketConsumer):

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['secret_key']
        self.user_email = self.scope['url_route']['kwargs']['user_email']
        self.room_group_name = 'chat_customer_%s' % self.room_name + self.user_email
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        msg = text_data_json['message']
        u_id = text_data_json['user_id']

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': msg,
                'id': u_id,
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        u_id = event['id']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'id': u_id
        }))


class AlertEmployee(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['secret_key']
        self.employee_id = self.scope['url_route']['kwargs']['employee_id']
        self.room_group_name = 'chat_customer_%s' % self.room_name + self.employee_id
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):

        text_data_json = json.loads(text_data)
        last_ques = text_data_json['last_ques'],
        user_id = text_data_json['user_id'],
        emp_id = text_data_json['emp_id'],
        if last_ques == 'End Chat':
            note_id = 1
        else:
            user = User.objects.get(pk=emp_id[0])
            customer = Customer.objects.get(u_field=user_id[0])

            note = EmpNotification.objects.create(user=user, customer=customer, message=last_ques[0])
            note_number, created = EmpNotifyNumber.objects.get_or_create(
                user=user,
                defaults={'number': 1}
            )
            note_id = note.pk

            if not created:
                note_number.number += 1
                note_number.save()

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'last_ques': last_ques,
                'user_id': user_id,
                'note_id': note_id,
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        last_ques = event['last_ques'],
        user_id = event['user_id'],
        note_id = event['note_id'],

        last_ques_send = last_ques[0][0]
        user_id_send = user_id[0][0]
        note_id_send = note_id[0]

        # Send message to WebSocket
        self.send(text_data=json.dumps({

            'last_ques': last_ques_send,
            'user_id': user_id_send,
            'note_id': note_id_send,
        }))
