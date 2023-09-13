import json
from django.http import JsonResponse
from django.shortcuts import render

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
import requests
import json



def send_to_rasa(message):
    rasa_url = 'http://localhost:5005/webhooks/rest/webhook'
    payload = {
        'sender': 'user_id',
        'message': message
    }
    response = requests.post(rasa_url, json=payload)
    return response.json()


