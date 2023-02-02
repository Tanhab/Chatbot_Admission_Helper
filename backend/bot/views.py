

from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

import sys
sys.path.insert(0,'../')
from chatbot_model.Chatbot import GenericAssistant

@api_view(['GET','POST'])
def get_reply(request):
    
    if request.method == 'GET':
        return Response({
            'status': 200,
            'intent': "greetings",
            'message': request.data
        })
    elif request.method == 'POST':
        query = request.data 
        if(query):
            assistant = GenericAssistant(load=True)
            reply = assistant.request(query['question'])
            if float(reply['probability']) < 0.8:
                return Response({
                    "reply" : "Sorry, I am not clear what you want to know"
                },status=400,content_type="JSON") 
            else:
                return Response({
                    "tag": reply['tag'],
                    "reply" : reply['reply']
                },status=200)

    return HttpResponse("Hello, world. You're at the polls index.")
