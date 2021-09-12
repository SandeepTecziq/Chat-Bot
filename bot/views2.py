from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import ChatHistory, Customer, User, Company, Conversation, Question, ChatTitle, SurveyQuestion
from googletrans import Translator
from django.db.models import Q, Max
from .chatgui import bot_reply
from .forms2 import QuestionForm, OptionForm
import json
from .forms import RequiredFormSet
from django.forms import formset_factory
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse


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


def chat_map_questions(request, pk, slug):
    chat_title = get_object_or_404(ChatTitle, pk=pk, slug=slug)
    chat_title = ChatTitle.objects.filter(Q(pk=pk) & Q(slug=slug)).prefetch_related('questions',
                                                                                    'questions__options').first()
    question_form = QuestionForm(title_pk=chat_title.pk, initial={'chat_title': chat_title.pk})
    formset_class = formset_factory(OptionForm, max_num=1000, min_num=1, formset=RequiredFormSet)
    option_formset = formset_class(form_kwargs={'question_form_type': 'test'})

    context = {
        'chat_title': chat_title,
        'company': chat_title.company,
        'question_form': question_form,
        'option_formset': option_formset,
    }

    return render(request, 'bot/chat_map_questions.html', context)


def save_chat_questions(request, pk, slug):
    chat_title = ChatTitle.objects.filter(Q(pk=pk) & Q(slug=slug)).first()

    if chat_title:
        if request.method == 'POST':
            question_form = QuestionForm(request.POST, request.FILES, title_pk=chat_title.pk)
            if question_form.is_valid():
                max_number = SurveyQuestion.objects.filter(chat_title=chat_title).aggregate(
                                number=Max('number'))['number']
                ques_number = max_number + 1 if max_number else 1
                question_form_type = request.POST.get('question_form_type')
                if question_form_type in ['instruction', 'text-question']:
                    question_qry = question_form.save(commit=False)
                    question_qry.chat_title = chat_title
                    question_qry.number = ques_number
                    question_qry.save()
                    data = {
                        'status': True,
                    }
                elif question_form_type in ['text-option', 'image-carousel', 'carousel-option']:
                    if question_form_type:
                        formset_class = formset_factory(OptionForm, max_num=1000, min_num=1, formset=RequiredFormSet)
                        option_formset = formset_class(request.POST, request.FILES,
                                                       form_kwargs={'question_form_type': question_form_type})
                        if option_formset.is_valid():
                            question_qry = question_form.save(commit=False)
                            question_qry.chat_title = chat_title
                            question_qry.number = ques_number
                            question_qry.save()
                            for form in option_formset:
                                option_save = form.save(commit=False)
                                option_save.question = question_qry
                                option_save.save()

                            data = {
                                'status': True,
                            }
                        else:
                            err_list = {}
                            for form in option_formset:
                                err_json = json.loads(form.errors.as_json())
                                for i in err_json:
                                    strap = err_json[i][0]['message']
                                    err_list[i.capitalize()] = strap
                            data = {
                                'status': 'form_error',
                                'message': err_list
                            }
                    else:
                        data = {
                            'status': False,
                            'message': 'Form type is not provided.'
                        }
                else:
                    data = {
                        'status': False,
                        'message': 'Question form type is incorrect.'
                    }

            else:
                err_list = {}
                err_json = json.loads(question_form.errors.as_json())
                for i in err_json:
                    strap = err_json[i][0]['message']
                    err_list[i.capitalize()] = strap
                data = {
                    'status': 'form_error',
                    'message': err_list
                }

        else:
            data = {
                'status': False,
                'message': 'Invalid request type'
            }
    else:
        data = {
            'status': False,
            'message': 'Chat map id and slug is incorrect'
        }

    if data['status']:
        chat_title = ChatTitle.objects.filter(Q(pk=pk) & Q(slug=slug)).prefetch_related('questions',
                                                                                        'questions__options').first()
        context = {
            'chat_title': chat_title,
        }
        html = render_to_string('question-template/map_question.html', context=context, request=request)
        data['html'] = html

    return JsonResponse(data)


@login_required(login_url='user_login')
def remove_save_question(request, title_pk, question_pk):
    chat_title = ChatTitle.objects.filter(pk=title_pk).first()
    SurveyQuestion.objects.filter(Q(pk=question_pk) & Q(chat_title=chat_title)).delete()
    return HttpResponseRedirect(reverse('chat_map_questions', args=(chat_title.pk, chat_title.slug)))

