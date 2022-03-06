from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import ChatHistory, Customer, User, Company, Conversation, Question, ChatTitle, SurveyQuestion, \
    ServiceProvider, SurveyOptions, TimeSlots, BookedSlots, ProviderCategory
from googletrans import Translator
from django.db.models import Q, Max, Count
from .chatgui import bot_reply
from .forms2 import QuestionForm, OptionForm
import json
from .forms import RequiredFormSet
from django.forms import formset_factory
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_exempt
from .view_functions import send_booking_confirmation_mail, get_online_employees


def get_bot_reply_updated(request):
    if_testing = request.GET.get('if_testing')
    history_pk = request.GET.get('history_pk')
    dir_name = request.GET.get('dir_name')
    question = request.GET.get('question')
    secret_key = request.GET.get('secret_key')
    customer_id = request.GET.get('customer_id')
    user_lang = request.GET.get('user_lang')
    company = Company.objects.filter(secret_key=secret_key).first()
    if_trained = Question.objects.filter(Q(question_tag__company=company) & Q(if_trained=True)).exists()
    try:
        if if_trained:
            reply = bot_reply(question, dir_name)
        else:
            reply = 'System can not answer this question. Would you like to talk to our customer care service.'
    except:
        reply = 'System can not answer this question. Would you like to talk to our customer care service.'

    if reply == 'System can not answer this question. Would you like to talk to our customer care service.':
        get_answer = 'fail'
    else:
        get_answer = 'pass'
    if if_testing:
        data = {'status': True, 'reply': reply, 'get_answer': get_answer}
    else:
        if history_pk and dir_name and question and secret_key and customer_id and user_lang:
            history = ChatHistory.objects.filter(pk=history_pk).first()
            customer = Customer.objects.filter(u_field=customer_id).first()
            if history and company and customer:
                company_lang = company.language
                if company_lang != user_lang:
                    translate = Translator()
                    question = translate.translate(question, src=user_lang, dest=company_lang).text
                Conversation.objects.create(
                    history=history,
                    question=question,
                    answer=reply,
                )

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
    response = JsonResponse(data)
    if data['status']:
        response.set_cookie('incomplete_chat_history', history_pk, 600, httponly=True)
        response.set_cookie('user_lang', user_lang, 600, httponly=True)
        response.set_cookie('customer_id', customer_id, 600, httponly=True)
        response.set_cookie('secret_key', secret_key, 600, httponly=True)

    return response


def chat_map_questions(request, pk, slug):
    chat_title = get_object_or_404(ChatTitle, pk=pk, slug=slug)
    questions = SurveyQuestion.objects.filter(chat_title=chat_title).order_by('number').prefetch_related('options')
    question_form = QuestionForm(title_pk=chat_title.pk, initial={'chat_title': chat_title.pk})
    formset_class = formset_factory(OptionForm, max_num=1000, min_num=1, formset=RequiredFormSet)
    option_formset = formset_class(form_kwargs={'question_form_type': 'test'})
    repeat_parent = questions.annotate(total_child=Count('child_question')).filter(total_child__gte=2)
    repeat_option = SurveyOptions.objects.filter(question__chat_title=chat_title).annotate(
        total_child=Count('child_question')).filter(total_child__gte=2)

    context = {
        'chat_title': chat_title,
        'company': chat_title.company,
        'question_form': question_form,
        'option_formset': option_formset,
        'questions': questions,
        'repeat_parent': repeat_parent,
        'repeat_option': repeat_option,
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


def edit_chat_questions(request, pk):
    question = SurveyQuestion.objects.filter(pk=pk).first()

    if question:
        if request.method == 'POST':
            question_form = QuestionForm(request.POST, request.FILES, title_pk=question.chat_title.pk,
                                         instance=question)
            if question_form.is_valid():
                question_form_type = request.POST.get('question_form_type')
                if_options = SurveyOptions.objects.filter(question=question)
                if question.ans_type in ['I', 'T']:
                    question_form.save()
                    data = {
                        'status': True,
                    }
                else:
                    formset_class = formset_factory(OptionForm, max_num=1000, min_num=1, formset=RequiredFormSet)
                    option_formset = formset_class(request.POST, request.FILES,
                                                   form_kwargs={'question_form_type': question_form_type})
                    if option_formset.is_valid():
                        question_qry = question_form.save()
                        if_options.delete()
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
            'message': 'Incorrect question id.'
        }

    if data['status'] and data['status'] != 'form_error':
        chat_title = ChatTitle.objects.filter(pk=question.chat_title.pk).prefetch_related('questions',
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
    questions = SurveyQuestion.objects.filter(chat_title=chat_title)
    count = 1
    for i in questions:
        i.number = count
        i.save()
        count += 1
    return HttpResponseRedirect(reverse('chat_map_questions', args=(chat_title.pk, chat_title.slug)))


@login_required(login_url='user_login')
def sort_title_questions(request, title_pk):
    pk_list = request.GET.get('array')
    if pk_list:
        pk_list = pk_list.split(',')
        count = 1
        for i in pk_list:
            question = SurveyQuestion.objects.filter(Q(chat_title__pk=title_pk) & Q(pk=i)).first()
            if question:
                question.number = count
                question.save()
                count += 1
        data = {
            'status': True
        }
    else:
        data = {
            'status': False,
            'message': 'No new changes in question sequence.'
        }

    return JsonResponse(data)


@xframe_options_exempt
@login_required(login_url='user_login')
def bot_testing(request, secret_key, lang):
    try:
        translate = Translator()
        company = Company.objects.filter(secret_key=secret_key)
        if company:
            company = company[0]
        else:
            context = {
                'not_found': True,
            }
            return render(request, 'question-template/bot_inactive.html', context)

        if_booking_available = ServiceProvider.objects.filter(company=company).exists()
        company_name = company.name[:10] if len(company.name) > 10 else company.name
        dir_name = 'company_files/' + str(company.id) + '_' + company_name + '/'
        sentence_list = [company.bot_name, company.intro_ques, company.bot_title, 'Book Appointment', company.bot_ques,
                         company.bot_introduction]
        variable_list = ['bot_name', 'intro_ques', 'bot_title', 'appointment_title', 'bot_ques', 'bot_introduction']
        if lang == company.language:
            translated_dict = dict(zip(variable_list, sentence_list))
        else:
            translated_lines = translate.translate(sentence_list, src=company.language, dest=lang)
            translated_dict = dict(zip(variable_list, [i.text for i in translated_lines]))

        chat_titles = {}
        for i in company.company_chat_title.all():
            if i.active:
                if lang == company.language:
                    chat_titles[i.pk] = i.title
                else:
                    chat_titles[i.pk] = translate.translate(i.title, src=company.language, dest=lang).text

        static_list = ['We have sent confirmation mail. Please check.', 'Please wait for a moment...',
                       'Click on calendar icon to open calendar', 'Yes', 'No',
                       'We have saved your requirements. We will contact you ASAP. Would you like to ask anything else?',
                       'Please wait for 2 minutes. We will message you.', 'Click "Yes" to book this slot.',
                       'Your booking details:']
        static_title = ['confirmation_mail', 'please_wait', 'open_calender_line', 'choose_yes', 'choose_no',
                        'saved_requirements', 'wait_3_min', 'yes_to_book', 'booking_details']
        if lang != 'en':
            static_list_obj = translate.translate(static_list, src='en', dest=lang)
            static_list = [i.text for i in static_list_obj]
        static_dict = dict(zip(static_title, static_list))

        context = {
            'company_secret_key': secret_key,
            'company': company,
            'dir_name': dir_name,
            'translated_dict': translated_dict,
            'chat_titles': chat_titles,
            'static_dict': static_dict,
            'if_booking_available': if_booking_available,
            'not_found': False,
            'secret_key': secret_key,
            'bot_testing': True,
            'lang': lang,
        }
        if company.active:
            return render(request, 'bot/bot_testing.html', context)
        else:
            return render(request, 'question-template/bot_inactive.html')
    except:
        return render(request, 'bot/404_page.html')


def get_next_question(request, title_pk, question_pk, is_option):
    title = ChatTitle.objects.filter(pk=title_pk).first()
    if title:
        if question_pk == '0':
            question = SurveyQuestion.objects.filter(Q(chat_title=title) & Q(number=1)).first()
            if question:
                context = {
                    'question': question
                }
                html = render_to_string('bot/next_question.html', context=context, request=request)
                data = {
                    'status': True,
                    'html': html,
                    'ans_type': question.ans_type,
                    'title_pk': title_pk,
                    'question_pk': question.pk,
                }
                return JsonResponse(data)
            else:
                data = {
                    'status': 'last',
                    'message': 'Thank you for using this service!'
                }
                return JsonResponse(data)
        else:
            if is_option == 'correct':
                prt_option = SurveyOptions.objects.filter(pk=question_pk).first()
                if prt_option:
                    question = SurveyQuestion.objects.filter(prt_option=prt_option).first()
                    if not question:
                        question = SurveyQuestion.objects.filter(prt_question=prt_option.question).first()

                        if not question:
                            number = prt_option.question.number + 1
                            fltr = Q(chat_title=title) & Q(number__gte=number) & Q(prt_option__isnull=True) \
                                   & Q(prt_question__isnull=True)

                            question = SurveyQuestion.objects.filter(fltr).first()
                            if not question:
                                data = {
                                    'status': 'last',
                                    'message': 'Thank you for using this service!'
                                }
                                return JsonResponse(data)
                    context = {
                        'question': question
                    }
                    html = render_to_string('bot/next_question.html', context=context, request=request)
                    data = {
                        'status': True,
                        'html': html,
                        'ans_type': question.ans_type,
                        'title_pk': title_pk,
                        'question_pk': question.pk,
                    }
                    return JsonResponse(data)

                else:
                    data = {
                        'status': False,
                        'message': 'Oops! There is something wrong.'
                    }
            else:
                prt_question = SurveyQuestion.objects.filter(pk=question_pk).first()
                if prt_question:
                    question = SurveyQuestion.objects.filter(prt_question=prt_question).first()
                    if not question:
                        number = prt_question.number + 1
                        fltr = Q(chat_title=title) & Q(number__gte=number) & Q(prt_option__isnull=True) \
                               & Q(prt_question__isnull=True)

                        question = SurveyQuestion.objects.filter(fltr).first()
                        if not question:
                            data = {
                                'status': 'last',
                                'message': 'Thank you for using this service!'
                            }
                            return JsonResponse(data)
                    context = {
                        'question': question
                    }
                    html = render_to_string('bot/next_question.html', context=context, request=request)
                    data = {
                        'status': True,
                        'html': html,
                        'ans_type': question.ans_type,
                        'title_pk': title_pk,
                        'question_pk': question.pk,
                    }
                    return JsonResponse(data)

                else:
                    data = {
                        'status': False,
                        'message': 'Oops! There is something wrong.'
                    }
    else:
        data = {
            'status': False,
            'message': 'Oops! There is something wrong.'
        }

    return JsonResponse(data)


def book_selected_slot(request):
    slot_pk = request.GET.get('slot_pk')
    time = request.GET.get('time')
    u_id = request.GET.get('u_id')

    if slot_pk and time and u_id:
        slot = TimeSlots.objects.filter(pk=slot_pk).first()
        user = Customer.objects.filter(u_field=u_id).first()
        if slot and user:
            email = user.email
            name = user.name
            company = user.company
            owner = User.objects.filter(Q(company=company.parent_company) & Q(role='admin')).first()
            if_slot = BookedSlots.objects.filter(Q(date=time) & Q(slot=slot)).exists()
            if not if_slot:
                slot = BookedSlots.objects.create(date=time, slot=slot, name=name, email=email)
                if owner:
                    send_booking_confirmation_mail(email, name, owner.username, owner.email, slot.pk)
                data = {
                    'status': True,
                    'message': 'Selected slot has been booked.'
                }
            else:
                data = {
                    'status': False,
                    'message': 'This slot already has been booked. Please select another.'
                }

        else:
            data = {
                'status': False,
                'message': 'Data not provided. Please try again.'
            }
    else:
        data = {
            'status': False,
            'message': 'Data not provided. Please try again.'
        }

    return JsonResponse(data)


def get_provider_category(request):
    pk = request.GET.get('pk')
    if pk:
        company = Company.objects.filter(pk=pk).first()
        if company:
            categories = ProviderCategory.objects.filter(company=company)
            category_list = []
            for i in categories:
                category_list.append({'pk': i.pk, 'name': i.name})
            data = {
                'status': True,
                'data': category_list
            }
        else:
            data = {
                'status': False,
                'message': 'Incorrect BOt detail.'
            }
    else:
        data = {
            'status': False,
            'message': 'Bot detail not provided'
        }
    return JsonResponse(data)


def get_available_employees(request, company_pk):
    company = Company.objects.filter(pk=company_pk).first()
    if company:
        users = company.users.all()
        user = users.filter(Q(logged_in=True) & Q(available=True)).first()

        if user:
            user.available = False
            user.save()
            data = {
                'status': True,
                'emp_pk': user.pk
            }
        else:
            data = {
                'status': False,
            }

    else:
        data = {
            'status': 'not found',
            'message': 'Company not found.'
        }

    return JsonResponse(data)


def leave_human_chat(request):
    emp_id = request.GET.get('emp_id')
    if emp_id:
        User.objects.filter(pk=emp_id).update(available=True)

    data = {
        'status': True
    }
    return JsonResponse(data)


def check_previous_chat(request):
    old_chat = request.COOKIES.get('incomplete_chat_history')
    user_lang = request.COOKIES.get('user_lang')
    customer_id = request.COOKIES.get('customer_id')
    secret_key = request.COOKIES.get('secret_key')
    if old_chat and secret_key and customer_id and user_lang:
        chat_history = ChatHistory.objects.filter(pk=old_chat).first()
        if chat_history:
            room_url = HttpResponseRedirect(reverse('room', secret_key, user_lang, customer_id)).url
            data = {
                'status': True,
                'room_url': request.build_absolute_uri(room_url) + '?previous_chat='+old_chat
            }
        else:
            data = {
                'status': False,
            }
    else:
        data = {
            'status': False,
        }

    return JsonResponse(data)
