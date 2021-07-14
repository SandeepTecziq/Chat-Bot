from django.shortcuts import render
from django.http import JsonResponse
from .models import ChatHistory, Customer, User, Company, Conversation, Question
from googletrans import Translator
from django.db.models import Q
from .chatgui import bot_reply


def test_bot(request):
    secret_key = request.GET.get('bot-secret-key')

    context = {
        'secret_key': secret_key
    }
    return render(request, 'bot/test_bot.html', context)


def get_bot_reply_updated(request):
    history_pk = request.GET.get('history_pk')
    dir_name = request.GET.get('dir_name')
    question = request.GET.get('question')
    secret_key = request.GET.get('secret_key')
    customer_id = request.GET.get('customer_id')
    user_lang = request.GET.get('user_lang')

    if history_pk and dir_name and question and secret_key and customer_id and user_lang:
        history = ChatHistory.objects.filter(pk=history_pk).first()
        company = Company.objects.filter(secret_key=secret_key).first()
        customer = Customer.objects.filter(u_field=customer_id).first()
        if history and company and customer:
            company_lang = company.language
            if company_lang != user_lang:
                translate = Translator()
                question = translate.translate(question, src=user_lang, dest=company_lang).text
            if_trained = Question.objects.filter(Q(question_tag__company=company) & Q(if_trained=True)).exists()

            try:
                if if_trained:
                    reply = bot_reply(question, dir_name)
                else:
                    reply = 'System can not answer this question. Would you like to talk to our customer care service.'
            except:
                reply = 'System can not answer this question. Would you like to talk to our customer care service.'

            Conversation.objects.create(
                history=history,
                question=question,
                answer=reply,
            )

            if reply == 'System can not answer this question. Would you like to talk to our customer care service.':
                get_answer = 'fail'
            else:
                get_answer = 'pass'

            if company_lang != user_lang:
                reply = translate.translate(reply, src=company_lang, dest=user_lang).text

            data = {'status': True, 'reply': reply, 'get_answer': get_answer}
        else:
            data = {
                'status': False,
                'message': 'Queries are required'
            }

    else:
        data = {
            'status': False,
            'message': 'All fields are required'
        }
    return JsonResponse(data)





