from django.shortcuts import render, get_object_or_404, HttpResponse, redirect
from .models import *
from .forms import *
from .forms2 import *
import json
from django.forms import formset_factory
from .train_chatbot import train_chat
from pathlib import Path
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, Count
from django.core.mail import send_mail
from django.contrib.auth import logout, login
import datetime
from django.template.loader import render_to_string
import googletrans
from googletrans import Translator
from .view_functions import get_all_detail, check_trained_status
import random
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from bot_api.common_view_function import start_chat_view, service_provider_view, get_slots, book_selected_slot_view, \
    get_title_pk


@login_required(login_url='user_login')
def update_bot_detail(request, id, bot_name):
    company = get_object_or_404(Company, pk=id, name=bot_name)

    if request.user.role != 'admin' and request.user.company.pk != company.parent_company.pk:
        return render(request, 'bot/check_user.html')

    form = UpdateBotForm(instance=company)
    if request.method == 'POST':

        form = UpdateBotForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('update_bot_detail', args=(id, bot_name)))

    context = {
        'form': form,
        'company': company,
        'update_bot_detail': 'active',
    }

    return render(request, 'bot/update_bot_detail.html', context)


def intro_change_language(request):

    intro_text = request.GET.get('intro_text', None)
    instruction_text = request.GET.get('instruction_text', None)
    selected = request.GET.get('selected', None)
    curr_lang = request.GET.get('curr_lang', None)
    if intro_text and instruction_text and selected:
        translator = Translator()
        intro_text = translator.translate(intro_text, src=curr_lang, dest=selected).text
        name_key = translator.translate('Name', src=curr_lang, dest=selected).text
        email_key = translator.translate('email', src=curr_lang, dest=selected).text
        start_chat_key = translator.translate('Start Chat', src=curr_lang, dest=selected).text
        instruction_text = translator.translate(instruction_text, src=curr_lang, dest=selected).text
        data = {
            'status': True,
            'instruction_text': instruction_text,
            'intro_text': intro_text,
            'name_key': name_key,
            'email_key': email_key,
            'start_chat_key': start_chat_key,
        }
    else:
        data = {
            'status': False
        }
    return JsonResponse(data)


def index(request):
    context = {

    }
    return render(request, 'home/homepage.html', context)


def pricing(request):
    context = {

    }
    return render(request, 'home/pricing.html', context)


def solutions(request):
    context = {

    }
    return render(request, 'home/solutions.html', context)


def templates(request):
    context = {

    }
    return render(request, 'home/templates.html', context)


@xframe_options_exempt
@csrf_exempt
def get_user_detail(request, secret_key):
    languages = googletrans.LANGUAGES
    form = CustomerForm()
    company = Company.objects.filter(secret_key=secret_key)
    if company:
        company = company[0]
    else:
        context = {
            'not_found': True,
        }
        return render(request, 'question-template/bot_inactive.html', context)

    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            name = form.cleaned_data['name']
            lang = request.POST['language-selected']
            # secret_key = form.cleaned_data['secret_key']
            company = Company.objects.get(secret_key=secret_key)
            customer, created = Customer.objects.get_or_create(
                email=email,
                company=company,
                defaults={'name': name}
            )
            u_id = customer.u_field

            return HttpResponseRedirect(reverse('room', args=(secret_key, lang, u_id)))

    context = {
        'form': form,
        'company': company,
        'languages': languages,
        'secret_key': secret_key,
        'not_found': False,
    }

    if company.active:
        return render(request, 'bot/get_user_detail.html', context)
    else:
        return render(request, 'question-template/bot_inactive.html', context)


@xframe_options_exempt
def room(request, secret_key, lang, u_id):
    try:
        translate = Translator()
        company = Company.objects.filter(secret_key=secret_key)
        customer = get_object_or_404(Customer, u_field=u_id)
        if company:
            company = company[0]
        else:
            context = {
                'not_found': True,
            }
            return render(request, 'question-template/bot_inactive.html', context)
        ChatHistory.objects.filter(Q(company=company) & Q(customer=customer)).update(saved_status=True)
        talker = User.objects.filter(Q(company=company.parent_company) & Q(role='admin')).first()
        new_history = ChatHistory.objects.create(company=company, customer=customer,
                                                 chat_type='bot_chat', talker=talker)

        if_booking_available = ServiceProvider.objects.filter(company=company).exists()
        company_name = company.name[:10] if len(company.name) > 10 else company.name
        dir_name = 'company_files/' + str(company.id) + '_' + company_name + '/'
        sentence_list = [company.bot_name, company.intro_ques, company.bot_title, 'Book Appointment', company.bot_ques]
        variable_list = ['bot_name', 'intro_ques', 'bot_title', 'appointment_title', 'bot_ques']
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
            'u_id': u_id,
            'lang': lang,
            'translated_dict': translated_dict,
            'chat_titles': chat_titles,
            'static_dict': static_dict,
            'if_booking_available': if_booking_available,
            'not_found': False,
            'new_history': new_history,
            'secret_key': secret_key,
        }
        if company.active:
            # return render(request, 'bot/room.html', context)
            return render(request, 'bot/chat_page.html', context)
        else:
            return render(request, 'question-template/bot_inactive.html')
    except:
        return render(request, 'bot/404_page.html')


# For Employee
@login_required(login_url='user_login')
def room_customer(request, secret_key, u_id, ques):
    company_qry = get_object_or_404(ParentCompany, secret_key=secret_key)
    if request.user.role != 'employee' and request.user.company.pk != company_qry.pk:
        return render(request, 'bot/check_user.html')

    user = request.user
    notification = EmpNotification.objects.filter(Q(user=user)).order_by('-pk')
    note_no = EmpNotifyNumber.objects.filter(user=user)
    note_number = note_no[0].number if note_no else 0
    customer_name = Customer.objects.get(u_field=u_id).name
    context = {
        'secret_key': secret_key,
        'company_qry': company_qry,
        'u_id': user.username,
        'uu_id': u_id,
        'customer_name': customer_name,
        'ques': ques,
        'notification': notification,
        'note_number': note_number,
    }
    return render(request, 'bot/room_customer.html', context)


@login_required(login_url='user_login')
def add_Question(request, id, bot_name):
    company = get_object_or_404(Company, pk=id, name=bot_name)

    if request.user.role != 'admin' and request.user.company.pk != company.parent_company.pk:
        return render(request, 'bot/check_user.html')

    all_saved = Question.objects.filter(Q(question_tag__company=company) & Q(if_trained=False)).exists()
    create_formset = formset_factory(AddQuestionForm, max_num=1000, formset=RequiredFormSet)
    if request.method == 'POST':
        formset = create_formset(request.POST)
        if formset.is_valid():
            for form in formset:
                tag = form.cleaned_data['tag']
                answer = form.cleaned_data['answer']
                list_quest = form.cleaned_data['question'].split('\r\n')
                if not tag:
                    tag = list_quest[0]
                question = {'question': list_quest}
                question_tag = QuestionTag.objects.create(tag=tag, company=company)
                question = Question.objects.create(question_tag=question_tag, question_text=question)
                Answer.objects.create(answer_text=answer, question=question, question_tag=question_tag,
                                      customer_care=request.user)

            return HttpResponseRedirect(reverse('notify', args=(id, bot_name)))

    else:
        formset = create_formset()

    context = {
        'notify': 'active',
        'formset': formset,
        'id': id,
        'company': company,
        'all_saved': all_saved,
    }

    return render(request, 'bot/add_question.html', context)


@login_required(login_url='user_login')
def create_file(request):
    pk = request.GET.get('pk')
    company = Company.objects.filter(pk=pk)
    if company:
        company = company[0]
    else:
        data = {
            'status': 'not_found',
            'message': 'Something went wrong. Please refresh and try again.'
        }
        return JsonResponse(data)

    if company.company_tag.count() < 2:
        data = {
            'status': 'less_2',
            'message': 'Need atleast 2 questions to train the bot.'
        }
        return JsonResponse(data)

    company_name = company.name[:10] if len(company.name) > 10 else company.name
    dir_name = 'company_files/' + str(company.id) + '_' + company_name + '/'
    filename = dir_name + 'fil.json'
    Path(dir_name).mkdir(parents=True, exist_ok=True)
    a = {'intents': []}
    qry = QuestionTag.objects.filter(company=company).prefetch_related('question_tag_name', 'answer_tag_name')

    for i in qry:
        dct = {'tag': i.tag, 'question': i.question_tag_name.question_text['question'],
               'answer': [i.answer_tag_name.answer_text]
               }
        a['intents'].append(dct)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(a, f, ensure_ascii=False, indent=4)

    train_chat(dir_name)
    messages.success(request, 'Bot has been trained')
    data = {
        'message': 'Bot has been trained successfully.',
        'status': True,
    }
    Question.objects.filter(question_tag__company=company).update(if_trained=True)
    return JsonResponse(data)


@login_required(login_url='user_login')
def question_list(request):
    if request.user.role != 'admin':
        return render(request, 'bot/check_user.html')
    parent_company = request.user.company
    deleted = False
    edited = False
    questions = Question.objects.filter(question_tag__company__parent_company=parent_company).prefetch_related('question_name')

    if request.method == 'POST' and 'edit-question-submit' in request.POST:
        form = AddQuestionForm(request.POST)
        if form.is_valid():
            tag = form.cleaned_data['tag']
            answer = form.cleaned_data['answer']
            question_id = request.POST['question-pk']
            list_quest = form.cleaned_data['question'].split('\r\n')
            curr_ques = Question.objects.get(pk=question_id)
            if not tag:
                tag = list_quest[0]
            question = {'question': list_quest}
            question_tag = QuestionTag.objects.filter(question_tag_name__pk=question_id).update(tag=tag)
            questions = Question.objects.filter(pk=question_id).update(question_text=question)
            answer = Answer.objects.filter(question=curr_ques).update(answer_text=answer)
            edited = True
            questions = Question.objects.filter(question_tag__company__parent_company=parent_company).prefetch_related(
                'question_name')

    elif request.method == 'POST':
        action = request.POST.get('change-status-select')
        items = request.POST.get('selected-items-input', None)
        if items:
            items = items.split(',')
            for i in items:
                title = Question.objects.get(pk=i)
                if title.question_tag.company.parent_company == parent_company:
                    if action == '1':
                        title.question_tag.delete()
                        deleted = True

    context = {
        'question_list': 'active',
        'questions': questions,
        'deleted': deleted,
        'edited': edited,
        'secret_key': parent_company.secret_key,
    }

    return render(request, 'bot/question_list.html', context)


@login_required(login_url='user_login')
def question_detail(request):
    secret_key = request.GET.get('secret_key')
    question_id = request.GET.get('question_id')
    company = ParentCompany.objects.get(secret_key=secret_key)

    if request.user.company != company:
        data = {
            'status': 'wrong_user',
            'message': 'Something went wrong. Please refresh and try again'
        }
        return JsonResponse(data)

    questions = Question.objects.filter(pk=question_id).prefetch_related('question_name')[0]
    data = questions.question_text['question']

    pre_field = '\r\n'.join(data)
    fields = {'question': pre_field, 'answer': questions.question_name.answer_text}
    form = AddQuestionForm(initial=fields)
    if request.is_ajax():
        context = {
            'form': form,
        }
        html = render_to_string('bot/question_detail.html', context=context, request=request)
        data = {
            'html': html,
            'status': True,
            'question_id': question_id,
        }

    else:
        data = {
            'status': False,
        }
    return JsonResponse(data)


@login_required(login_url='user_login')
def chat_history(request):
    if request.user.role != 'admin':
        return render(request, 'bot/check_user.html')

    parent_company = request.user.company

    qry_filter = Q(company__parent_company=parent_company)
    histories = ChatHistory.objects.filter(qry_filter).annotate(q_count=Count('chat_history'))

    context = {
        'chat_history': 'active',
        'histories': histories,
        'secret_key': parent_company.secret_key
    }
    return render(request, 'bot/chat_history.html', context)


@login_required(login_url='user_login')
def get_conversation(request, secret_key, id):
    # secret key is company's secret key
    if request.user.role != 'admin':
        return render(request, 'bot/check_user.html')

    conversation = Conversation.objects.filter(history__pk=id)
    company_secret_key = conversation[0].history.company.secret_key
    context = {
        'get_conversation': 'active',
        'conversation': conversation,
        'id': id,
        'company_secret_key': company_secret_key,
    }
    return render(request, 'bot/chat_conversation.html', context)


@login_required(login_url='user_login')
def remove_note(request):
    note_type = request.GET.get('note_type')
    secret_key = request.GET.get('secret_key')
    company = get_object_or_404(ParentCompany, secret_key=secret_key)
    NotifyNumber.objects.filter(Q(company__parent_company=company) & Q(note_type=note_type)).update(number=0)
    data = {
        'success': True
    }

    return JsonResponse(data)


@login_required(login_url='user_login')
def change_read_status_note(request):
    pk = request.GET.get('pk')
    Notification.objects.filter(pk=pk).update(read_status=True)
    data = {
        'changed': True
    }

    return JsonResponse(data)


def user_login(request):
    form = UserLoginForm()
    forget_password_form = ForgetPasswordForm()
    parent_company_form = ParentCompanyForm()
    signup_form = CreateUserForm()
    signup_success = True
    action = request.GET.get('action')
    if request.method == 'POST' and 'login-submit' in request.POST:
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.login(request)
            if user:
                login(request, user)
                next_page = request.GET.get('next')
                if user.is_staff and user.is_superuser:
                    return HttpResponseRedirect(reverse('company_list'))

                secret_key = user.company.secret_key
                if user.role == 'admin':
                    return HttpResponseRedirect(reverse('bot_list'))
                else:
                    return HttpResponseRedirect(reverse('employee_page', args=(secret_key,)))

    elif request.method == 'POST' and 'signup-submit' in request.POST:
        parent_company_form = ParentCompanyForm(request.POST)
        signup_form = CreateUserForm(request.POST)

        if parent_company_form.is_valid() and signup_form.is_valid():
            parent = parent_company_form.save(commit=True)
            user = signup_form.save(commit=False)
            user.set_password(signup_form.cleaned_data['password'])
            user.company = parent
            user.role = 'admin'
            user.save()
            subscription = SubscriptionPlan.objects.filter(is_default=True)
            expire_date = datetime.datetime.now() + datetime.timedelta(days=30)
            if subscription:
                subscription = subscription[0]
                number = subscription.bot_allowed
                TakenSubscription.objects.create(subscription=subscription, parent_company=parent, paid=True,
                                                 expire_date=expire_date, remaining_bot=number)
            else:
                subscription = SubscriptionPlan.objects.all()
                if subscription:
                    subscription = subscription[0]
                    number = subscription.bot_allowed
                    TakenSubscription.objects.create(subscription=subscription, parent_company=parent, paid=True,
                                                     expire_date=expire_date, remaining_bot=number)
            login(request, user)
            return HttpResponseRedirect(reverse('bot_list'))
        else:
            signup_success = False

    context = {
        'form': form,
        'forget_password_form': forget_password_form,
        'parent_company_form': parent_company_form,
        'signup_form': signup_form,
        'signup_success': signup_success,
        'action': action,
    }
    return render(request, 'bot/user_login.html', context)


def user_logout(request):
    logout(request)
    return redirect('user_login')


# For Employee
@login_required(login_url='user_login')
def employee_page(request, secret_key):
    if request.user.role != 'employee':
        return render(request, 'bot/check_user.html')
    user = request.user
    notification = EmpNotification.objects.filter(Q(read_status=False) & Q(user=user)).order_by('-pk')
    note_no = EmpNotifyNumber.objects.filter(user=user)
    note_number = note_no[0].number if note_no else 0
    context = {
        'user': user,
        'secret_key': secret_key,
        'notification': notification,
        'note_number': note_number,

    }

    return render(request, 'bot/employee_home.html', context)


@login_required(login_url='user_login')
def create_user(request):
    if request.user.role != 'admin':
        return render(request, 'bot/check_user.html')

    parent_company = request.user.company
    form = CreateUserForm()
    company_bots = Company.objects.filter(parent_company=parent_company)

    if request.method == 'POST' and 'add_bot_submit' in request.POST:
        user_pk = request.POST['user_pk']
        user = get_object_or_404(User, pk=user_pk)
        add_bot_form = AddBotToUser(request.POST)
        if add_bot_form.is_valid():
            user.bots.set(request.POST.getlist('add_bot_to_user'))
            user.save()

    elif request.method == 'POST' and 'signup_submit' in request.POST:
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user_form = form.save(commit=False)
            user_form.set_password(form.cleaned_data['password'])
            user_form.company = parent_company
            user_form.role = 'employee'
            user_form.save()
            user_form.bots.set(request.POST.getlist('add_bot_to_user'))
            user_form.save()
            return HttpResponseRedirect(reverse('create_user'))

    context = {
        'form': form,
        'create_user': 'active',
        'company_bots': company_bots,
    }
    return render(request, 'bot/create_user.html', context)


@login_required(login_url='user_login')
def add_bot_to_user(request):
    user_pk = request.GET.get('user_pk')
    user = get_object_or_404(User, pk=user_pk)
    company_bots = Company.objects.filter(parent_company=user.company)

    if request.is_ajax():
        form = AddBotToUser(instance=user)
        context = {
            'form': form,
            'user': user,
            'company_bots': company_bots,
        }
        html = render_to_string('question-template/add_bot_to_user.html', context=context, request=request)
        data = {
            'html': html,
            'status': True,
        }

    else:
        data = {
            'status': False,
            'message': 'Something went wrong. Please refresh and try again.'
        }
    return JsonResponse(data)


# For Employee
@login_required(login_url='user_login')
def remove_emp_notification(request):
    user_id = request.GET.get('user')
    user = get_object_or_404(User, pk=user_id)
    EmpNotifyNumber.objects.filter(user=user).update(number=0)
    data = {
        'success': True
    }

    return JsonResponse(data)


# For Employee
@login_required(login_url='user_login')
def change_emp_read_status_note(request):
    pk = request.GET.get('pk')
    EmpNotification.objects.filter(pk=pk).update(read_status=True)
    data = {
        'changed': True
    }

    return JsonResponse(data)


def save_chat_customer(request):
    chat = request.GET.get('message')
    secret_key = request.GET.get('secret_key')
    cust_id = request.GET.get('cust_id')
    is_bot = request.GET.get('is_bot', None)
    # company = Company.objects.get(secret_key=secret_key)
    customer = Customer.objects.get(u_field=cust_id)
    company = customer.company
    user = request.user
    chat_j = json.loads(chat)
    history = ChatHistory.objects.create(company=company, talker=user, customer=customer,
                                         chat_type='user_chat', saved_status=True, trained_status=False)

    if is_bot == 'yes':
        history.trained_status = True
        history.save()

    for key, value in chat_j.items():
        Conversation.objects.create(history=history, question=key, answer=value)

    data = {'success': True}
    return JsonResponse(data)


def train_chat_data(request):
    chat = request.GET.get('chat')
    secret_key = request.GET.get('secret_key')
    id = request.GET.get('id')
    username = request.GET.get('username')
    user = User.objects.get(username=username)
    company = Company.objects.get(secret_key=secret_key)
    chat_json = json.loads(chat)
    for i, j in chat_json.items():
        tag = QuestionTag.objects.create(tag=i, company=company)
        question = Question.objects.create(question_tag=tag, question_text={'question': [i]})
        Answer.objects.create(question_tag=tag, question=question, answer_text=j, customer_care=user)
    ChatHistory.objects.filter(pk=id).update(trained_status=True)
    data = {
        'message': 'Updated'
    }
    return JsonResponse(data)


@login_required(login_url='user_login')
def create_chat_map(request, id, bot_name):
    company = get_object_or_404(Company, pk=id, name=bot_name)

    if request.user.role != 'admin' and request.user.company.pk != company.parent_company.pk:
        return render(request, 'bot/check_user.html')

    chat_new_form = ChatNewForm()
    single_chat_form = SingleChatForm()
    carousel_chat_form = CarouselChatForm()

    context = {
        'chat_new_form': chat_new_form,
        'single_chat_form': single_chat_form,
        'carousel_chat_form': carousel_chat_form,
        'create_chat_map': 'active',
        'id': id,
        'company': company,
    }
    return render(request, 'bot/create_map.html', context)


def save_chat_name(request):
    if not request.user.is_authenticated:
        data = {
            'status': 'Invalid'
        }
        return JsonResponse(data)
    id = request.GET.get('id', None)
    name = request.GET.get('name', None)

    if not id:
        data = {
            'status': 'Invalid'
        }

        return JsonResponse(data)
    chat_title = ChatTitle.objects.filter(Q(company=Company.objects.get(pk=id)) & Q(title=name)).exists()

    if not name:
        data = {
            'status': False,
            'message': 'Please enter chat title.'
        }

    elif chat_title:
        data = {
            'status': False,
            'message': 'This chat title already has been registered.'
        }
    else:
        title = ChatTitle.objects.create(company=Company.objects.get(pk=id), title=name)
        data = {
            'status': True,
            'pk': title.pk,
        }
    return JsonResponse(data)


def edit_chat_name(request):
    if not request.user.is_authenticated:
        data = {
            'status': 'Invalid'
        }
        return JsonResponse(data)
    id = request.GET.get('id', None)
    name = request.GET.get('name', None)

    if not id:
        data = {
            'status': 'Invalid'
        }

        return JsonResponse(data)

    if not name:
        data = {
            'status': False,
            'message': 'Please enter chat name.'
        }

        return JsonResponse(data)

    chat_title = ChatTitle.objects.filter(pk=id)

    if not chat_title:
        data = {
            'status': 'Invalid',
        }
    else:
        company = chat_title[0].company
        title = ChatTitle.objects.filter(Q(company=company) & Q(title=name))
        if title and title[0].pk != chat_title[0].pk:
            data = {
                'status': False,
                'message': 'This chat name already has been registered.'
            }
            return JsonResponse(data)
        else:
            chat_title.update(title=name)
            data = {
                'status': True,
                'pk': chat_title[0].pk,
            }
    return JsonResponse(data)


def start_chat(request):
    main_type = request.GET.get('main_type')
    user_lang = request.GET.get('lang')
    title_pk = request.GET.get('title')
    option_number = request.GET.get('option_number')
    number = request.GET.get('number')
    data = get_title_pk(main_type, title_pk, option_number, number)

    if data['status'] == False or data['status'] == 'end_chat':
        return JsonResponse(data)

    title_pk = data['title_pk']
    #
    #
    #
    # title_qry = get_object_or_404(ChatTitle, pk=title_pk)
    #
    # if main_type == 'start':
    #     chat_title = ChatQuestionNew.objects.filter(Q(chat_title=title_qry) & Q(number=1))
    #     if not chat_title:
    #         data = {
    #             'status': False,
    #             'message': 'Chatmap does not exists.'
    #         }
    #         return data
    #     else:
    #         chat_title = chat_title[0]
    #     title_pk = chat_title.pk
    #
    # elif main_type == 'next':
    #
    #     if option_number == 'false':
    #         chat_title = ChatQuestionNew.objects.filter(Q(chat_title=title_qry) & Q(parent=number))
    #         if chat_title:
    #             chat_title = chat_title[0]
    #         else:
    #             data = {
    #                 'status': 'end_chat',
    #             }
    #             return JsonResponse(data)
    #     else:
    #         chat_title_option = ChatQuestionNew.objects.filter(Q(chat_title=title_qry) & Q(parent=option_number))
    #         chat_title_text = ChatQuestionNew.objects.filter(Q(chat_title=title_qry) & Q(parent=number))
    #         if chat_title_option:
    #             chat_title = chat_title_option[0]
    #
    #         elif chat_title_text:
    #             chat_title = chat_title_text[0]
    #
    #         else:
    #             data = {
    #                 'status': 'end_chat',
    #             }
    #             return JsonResponse(data)
    #
    #     title_pk = chat_title.pk
    #
    # else:
    #     data = {
    #         'status': False,
    #         'message': 'Invalid request number 2. Please refresh and try again.'
    #     }
    #     return JsonResponse(data)

    question_data = start_chat_view(title_pk, user_lang)
    if request.is_ajax():
        context = {
            'question_data': question_data,
        }
        if question_data['carousel_type'] == 'single':
            html = render_to_string('question-template/single.html', context, request=request)
        elif question_data['carousel_type'] == 'carousel':
            html = render_to_string('question-template/carousel.html', context, request=request)

        data = {
            'html': html,
            'status': True,
            'is_option': question_data['is_option'],
            'title-pk': question_data['title_pk']
        }
    else:
        data = {
            'status': False,
            'message': 'Invalid request type.'
        }

    return JsonResponse(data)


@login_required(login_url='user_login')
def admin_dashboard(request):
    company = request.user.company


@login_required(login_url='user_login')
def bot_list(request):
    if request.user.role != 'admin':
        return render(request, 'bot/check_user.html')
    parent_company = request.user.company
    bots = Company.objects.filter(parent_company=parent_company)
    subscription_plans = SubscriptionPlan.objects.all()
    allowed_bot = TakenSubscription.objects.filter(Q(parent_company=parent_company) & Q(paid=True)).aggregate(sum=Sum('remaining_bot'))
    context = {
        'bots': bots,
        'subscription_plans': subscription_plans,
        'bot_list': 'active',
        'allowed_bot': allowed_bot,
    }

    return render(request, 'bot/all_bots.html', context)


@login_required(login_url='user_login')
def add_bot(request):
    if request.user.role != 'admin':
        return render(request, 'bot/check_user.html')

    form = CreateCompany()
    if request.method == 'POST':
        form = CreateCompany(request.POST, request.FILES)
        if form.is_valid():
            save_bot = form.save(commit=False)
            save_bot.parent_company = request.user.company
            save_bot.save()
            return HttpResponseRedirect(reverse('bot_list'))

    context = {
        'add_bot': 'active',
        'form': form,
    }

    return render(request, 'bot/add_bot.html', context)


@login_required(login_url='user_login')
def chat_maps(request, id, name):
    company = get_object_or_404(Company, pk=id, name=name)

    if request.user.role != 'admin' and request.user.company.pk != company.parent_company.pk:
        return render(request, 'bot/check_user.html')

    company = get_object_or_404(Company, pk=id, name=name)
    ChatTitle.objects.filter(question_titles__isnull=True).update(active=False)
    chat_title = ChatTitle.objects.filter(Q(company=company))

    context = {
        'chat_maps': 'active',
        'chat_title': chat_title,
        'company': company,
    }
    return render(request, 'bot/chat_maps.html', context)


@login_required(login_url='user_login')
def delete_chat_title(request, id):
    title = ChatTitle.objects.filter(pk=id)[0]
    company_pk = title.company.pk
    company_name = title.company.name
    secret_key = title.company.parent_company.secret_key
    if request.user.company.secret_key != secret_key:
        return render(request, 'bot/check_user.html')
    title.delete()

    return HttpResponseRedirect(reverse('chat_maps', args=(company_pk, company_name)))


@login_required(login_url='user_login')
def create_service_provider(request):
    if request.user.role != 'admin':
        return render(request, 'bot/check_user.html')

    parent_company = request.user.company
    service_providers = ServiceProvider.objects.filter(company__parent_company=parent_company).prefetch_related('provider_slot')
    if service_providers:
        curr_provider = service_providers[0]
    else:
        curr_provider = None
    time_slot_form = TimeSlotForm()
    create_provider_form = CreateProviderForm()

    context = {
        'create_provider_form': create_provider_form,
        'service_providers': service_providers,
        'curr_provider': curr_provider,
        'time_slot_form': time_slot_form,
        'parent_company': parent_company,
        'create_service_provider': 'active',
    }
    return render(request, 'bot/create_service_provider.html', context)


@login_required(login_url='user_login')
def add_provider_in_list(request):
    if request.method == 'POST':
        form = CreateProviderForm(request.POST)
        if form.is_valid():
            parent_company = request.user.company
            provider = form.save(commit=False)
            company_pk = request.POST.get('select-bot-name', None)
            if not company_pk:
                data = {
                    'status': False,
                    'message': 'Please select Bot Name'
                }
                return JsonResponse(data)
            provider_company = Company.objects.filter(pk=company_pk)
            if not provider_company or provider_company[0].parent_company.pk != parent_company.pk:
                data = {
                    'status': False,
                    'message': 'Incorrect Bot Name selected'
                }
                return JsonResponse(data)
            provider_company = provider_company[0]
            provider.company = provider_company
            provider.save()

            if request.is_ajax():
                service_providers = ServiceProvider.objects.filter(company__parent_company=parent_company).prefetch_related('provider_slot')
                context_provider = {
                    'service_providers': service_providers,
                }

                context_slot = {
                    'curr_provider': provider,
                }
                html = render_to_string('bot/provider-list.html', context_provider, request=request)
                html2 = render_to_string('bot/create_time_slot.html', context_slot, request=request)

                data = {
                    'html': html,
                    'html2': html2,
                    'status': True,
                }
            else:
                data = {
                    'status': False,
                    'message': 'bad request. Please refresh and try again.'
                }
        else:
            data = {
                'status': False,
                'message': 'Input type is not correct.'
            }
    else:
        data = {
            'status': False,
            'message': 'Bad submission method. Please refresh and try again.'
        }
    return JsonResponse(data)


@login_required(login_url='user_login')
def provider_detail(request):
    pk = request.GET.get('pk')
    service_providers = ServiceProvider.objects.filter(pk=pk).prefetch_related('provider_slot')
    if service_providers:
        curr_provider = service_providers[0]

        if request.is_ajax():
            context = {
                'curr_provider': curr_provider,

            }
            html = render_to_string('bot/create_time_slot.html', context, request=request)
            data = {
                'html': html,
                'status': True,
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


@login_required(login_url='user_login')
def create_time_slot(request):
    if request.method == 'POST':
        user_pk = request.POST['provider']
        start = request.POST['start']
        end = request.POST['end']
        day = request.POST.getlist('select-day-drop-down')
        if start and end and user_pk and day:
            providers = ServiceProvider.objects.filter(pk=user_pk)
            if providers:
                curr_provider = providers[0]
                start = datetime.datetime.strptime(start, '%H:%M').time()
                end = datetime.datetime.strptime(end, '%H:%M').time()
                if start >= end:
                    data = {
                        'status': False,
                        'message': 'start time should be less than end time.'
                    }
                else:
                    TimeSlots.objects.create(start=start, end=end, day={'day': day}, provider=curr_provider)
                    curr_provider = ServiceProvider.objects.filter(pk=user_pk).prefetch_related('provider_slot')[0]
                    if request.is_ajax():
                        context = {
                            'curr_provider': curr_provider,
                        }
                        html = render_to_string('bot/create_time_slot.html', context, request=request)
                        data = {
                            'html': html,
                            'status': True,
                        }
                    else:
                        data = {
                            'status': False,
                            'message': 'Something went wrong. Please refresh and try again.'
                        }
            else:
                data = {
                    'status': False,
                    'message': 'Something went wrong. Please refresh and try again.'
                }
        else:
            data = {
                'status': False,
                'message': 'All fields are required.'
            }
    else:
        data = {
            'status': False,
            'message': 'Something went wrong. Please refresh and try again.'
        }

    return JsonResponse(data)


def change_provider_state(request):
    pk = request.GET.get('pk', None)
    name = request.GET.get('name', None)

    provider = ServiceProvider.objects.filter(Q(pk=pk) & Q(name=name))
    if not provider:
        data = {
            'status': False,
            'message': 'Incorrect provider detail'
        }
        return JsonResponse(data)
    if provider[0].is_active:
        provider.update(is_active=False)
    else:
        provider.update(is_active=True)

    if request.is_ajax:
        context = {
            'curr_provider': provider[0]
        }

        html = render_to_string('bot/create_time_slot.html', context, request=request)
        data = {
            'html': html,
            'status': True,
        }
    else:
        data = {
            'status': False,
            'message': 'Incorrect request type.'
        }

    return JsonResponse(data)


@login_required(login_url='user_login')
def change_password(request):
    form = ChangePasswordForm(request.POST)
    if form.is_valid():
        user = request.user
        password = form.cleaned_data['password']
        user.set_password(password)
        user.password_changed = True
        user.save()
        data = {
            'status': True,
        }

    else:
        message = ''
        for field, errors in form.errors.items():
            message = errors
        data = {
            'status': False,
            'message': message,
        }

    return JsonResponse(data)


@login_required(login_url='user_login')
def company_list(request):
    if request.user.is_staff == False or request.user.is_superuser == False:
        return render(request, 'bot/check_user.html')
    companies = ParentCompany.objects.all().order_by('-pk').prefetch_related('company_name')
    context = {
        'companies': companies,
        'company_list': 'active',
    }

    return render(request, 'bot/company_list.html', context)


def forget_password(request):
    form = ForgetPasswordForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data['username']
        user = User.objects.get(username=username)
        password = User.objects.make_random_password()
        user.set_password(password)
        user.password_changed = True
        user.save()
        subject = 'Password Reset'
        mail_message = 'Password reset for username ' + username + ' is done. Please use ' + password + ' as password from now.'
        send_mail(
            subject,
            mail_message,
            'skeshari@tecziq.com',
            [user.email],
            fail_silently=False,
        )
        data = {
            'status': True,
        }

    else:
        message = ''
        for field, errors in form.errors.items():
            message = errors
        data = {
            'status': False,
            'message': message,
        }

    return JsonResponse(data)


@login_required(login_url='user_login')
def edit_chat_map(request, id, chat_title):
    # try:
    chat_title = get_object_or_404(ChatTitle, pk=id, title=chat_title)
    maps = ChatQuestionNew.objects.filter(chat_title=chat_title).prefetch_related('single_chat_question', 'carousel_chat_question')

    company = chat_title.company
    if request.user.role != 'admin' and request.user.company.pk != company.parent_company.pk:
        return render(request, 'bot/check_user.html')

    chat_new_form = ChatNewForm()
    single_chat_form = SingleChatForm()
    carousel_chat_form = CarouselChatForm()

    context = {
        'maps': maps,
        'chat_new_form': chat_new_form,
        'single_chat_form': single_chat_form,
        'carousel_chat_form': carousel_chat_form,
        'company': company,
        'chat_title': chat_title,
    }

    return render(request, 'bot/edit_chat_map.html', context)


def save_question(request):
    if request.method == 'POST':
        chat_new_form = ChatNewForm(request.POST)
        if chat_new_form.is_valid():
            question = chat_new_form.cleaned_data['question']
            chat_title = chat_new_form.cleaned_data['chat_title']
            number = chat_new_form.cleaned_data['number']
            parent = chat_new_form.cleaned_data.get('parent', None)
            carousel_type = chat_new_form.cleaned_data.get('carousel_type', None)
            u_id = chat_new_form.cleaned_data.get('u_id', None)
            is_option = chat_new_form.cleaned_data.get('is_option', None)
            form_type = chat_new_form.cleaned_data.get('form_type', None)
            is_first = True if number == "1" else False
            option = True if is_option == "True" else False
            title = ChatTitle.objects.filter(pk=chat_title)
            if title:
                title = title[0]
            else:
                data = {
                    'status': False,
                    'message': "Something went wrong. Please refresh and try again."
                }
                return JsonResponse(data)
            new_ques = ChatQuestionNew.objects.create(
                text=question, number=number, carousel_type=carousel_type, chat_title=title, is_option=option,
                is_first=is_first, parent=parent, form_type=form_type
            )
            if u_id:
                new_ques.u_id = u_id
                new_ques.save()
            child_id = new_ques.child_id
            if carousel_type == 'single':
                single_chat_form = SingleChatForm(request.POST, request.FILES)
                if single_chat_form.is_valid():
                    image = single_chat_form.cleaned_data.get('image', None)
                    url = single_chat_form.cleaned_data.get('url', None)
                    text = single_chat_form.cleaned_data.get('single_text', None)
                    desc = single_chat_form.cleaned_data.get('description', None)
                    if form_type == 'card-form' or form_type == 'card-option-form':
                        if not desc:
                            data = {
                                'status': False,
                                'message': 'Card Body is required'
                            }
                            new_ques.delete()
                            return JsonResponse(data)

                    ques_detail = SingleChatQuestion.objects.create(chat_title=new_ques, url=url, image=image,
                                                                    single_text=text, description=desc)
                    data = {
                        'status': True,
                        'child_id': child_id,
                        'number': number,
                        'single_option': False,
                        'carousel_option': False,
                        'new_pk': new_ques.pk,
                    }
                    if option:
                        option_number = request.POST.getlist('option-number-name')
                        option_values = request.POST.getlist('option-text-name')
                        for i in option_values:
                            if not i:
                                data = {
                                    'status': False,
                                    'message': 'All options are required'
                                }
                                new_ques.delete()
                                return JsonResponse(data)
                        option_values = [[i] for i in option_values]
                        option_dict = dict(zip(option_number, option_values))
                        for i in option_dict:
                            new_id = str(uuid.uuid4())
                            option_dict[i].append(new_id)
                        ques_detail.options = option_dict
                        ques_detail.save()
                        data['options'] = option_dict
                        data['single_option'] = True

                    return JsonResponse(data)
                else:
                    pass

            elif carousel_type == 'carousel':
                carousel_chat_form = CarouselChatForm(request.POST, request.FILES)
                images = request.FILES.getlist('image')
                texts = request.POST.getlist('text')
                numbers = request.POST.getlist('number_option')
                description = request.POST.getlist('description')
                item_number = int(request.POST.get('total-item-number'))
                if form_type == 'card-carousel-form' or form_type == 'card-carousel-option-form':
                    for i in description:
                        if not i:
                            data = {
                                'status': False,
                                'message': 'Card Body is required'
                            }
                            new_ques.delete()
                            return JsonResponse(data)

                if form_type == 'image-carousel-form' or form_type == 'image-carousel-option-form':

                    if len(images) != item_number:

                        data = {
                            'status': False,
                            'message': 'Image field is required'
                        }
                        new_ques.delete()
                        return JsonResponse(data)

                data = {
                    'status': True,
                    'child_id': child_id,
                    'number': number,
                    'single_option': False,
                    'carousel_option': False,
                    'new_pk': new_ques.pk,
                }
                if option:
                    options = request.POST.getlist('option')
                    for i in options:
                        if not i:
                            data = {
                                'status': False,
                                'message': 'All options are required'
                            }
                            new_ques.delete()
                            return JsonResponse(data)
                    carousel_option_dict = {}
                for i in range(item_number):
                    chat_n = CarouselChatQuestion.objects.create(chat_title=new_ques, text=texts[i], description=description[i])
                    try:
                        chat_n.image = images[i]
                    except:
                        pass
                    try:
                        chat_n.number = numbers[i]
                    except:
                        pass

                    if option:
                        chat_n.option = options[i]
                        new_id = str(uuid.uuid4())
                        chat_n.child_id = new_id
                        carousel_option_dict[chat_n.number] = new_id
                    chat_n.save()

                if option:
                    data['carousel_option'] = True
                    data['carousel_option_dict'] = carousel_option_dict
                return JsonResponse(data)

        else:
            err_list = []
            err_json = json.loads(chat_new_form.errors.as_json())
            for i in err_json:
                strap = i + ': ' + err_json[i][0]['message']
                err_list.append(strap)
            data = {
                'status': 'form_error',
                'message': err_list
            }

            return JsonResponse(data)
    else:
        data = {
            'status': False,
            'message': "Method get"
        }
    return JsonResponse(data)


@login_required(login_url='user_login')
def edit_save_question(request):
    if request.method == 'POST':
        chat_new_form = ChatNewForm(request.POST)
        if chat_new_form.is_valid():
            question = chat_new_form.cleaned_data['question']
            chat_map_pk = int(request.POST['current-map-pk'])
            chat_title = chat_new_form.cleaned_data['chat_title']
            number = chat_new_form.cleaned_data['number']
            parent = chat_new_form.cleaned_data.get('parent', None)
            # u_id = chat_new_form.cleaned_data.get('u_id', None)
            is_first = True if number == "1" else False
            chat_map = ChatTitle.objects.filter(pk=chat_title)
            if chat_map:
                chat_map = chat_map[0]
            else:
                data = {
                    'status': False,
                    'message': "Something went wrong. Please refresh and try again."
                }
                return JsonResponse(data)

            new_ques = ChatQuestionNew.objects.filter(pk=chat_map_pk)

            new_ques.update(text=question, number=number, is_first=is_first, parent=parent)
            new_ques = new_ques[0]

            # if u_id:
            #     new_ques.u_id = u_id
            #     new_ques.save()
            # child_id = new_ques.child_id
            if new_ques.carousel_type == 'single':
                single_chat_form = SingleChatForm(request.POST, request.FILES)
                if single_chat_form.is_valid():
                    image = single_chat_form.cleaned_data.get('image', None)
                    url = single_chat_form.cleaned_data.get('url', None)
                    text = single_chat_form.cleaned_data.get('single_text', None)
                    desc = single_chat_form.cleaned_data.get('description', None)
                    if new_ques.form_type == 'card-form' or new_ques.form_type == 'card-option-form':
                        if not desc:
                            data = {
                                'status': False,
                                'message': 'Card Body is required'
                            }
                            return JsonResponse(data)
                    ques_detail = SingleChatQuestion.objects.filter(chat_title=new_ques)
                    ques_detail.update(url=url, image=image, single_text=text, description=desc)
                    ques_detail = ques_detail[0]

                    data = {
                        'status': True,
                        # 'child_id': child_id,
                        'number': number,
                        'single_option': False,
                        'carousel_option': False
                    }
                    if new_ques.is_option:
                        option_number = request.POST.getlist('option-number-name')
                        option_values = request.POST.getlist('option-text-name')
                        for i in option_values:
                            if not i:
                                data = {
                                    'status': False,
                                    'message': 'All options are required'
                                }
                                return JsonResponse(data)
                        option_values = [[i] for i in option_values]
                        option_dict = dict(zip(option_number, option_values))
                        for i in option_dict:
                            # if option_dict[i] not in ques_detail.options:
                                new_id = str(uuid.uuid4())
                                option_dict[i].append(new_id)
                        ques_detail.options = option_dict
                        ques_detail.save()
                        data['options'] = option_dict
                        data['single_option'] = True

                    return JsonResponse(data)
                else:
                    pass

            elif new_ques.carousel_type == 'carousel':
                carousel_chat_form = CarouselChatForm(request.POST, request.FILES)
                images = request.FILES.getlist('image')
                image_count = request.POST.getlist('image-count', None)
                texts = request.POST.getlist('text')
                numbers = request.POST.getlist('number_option')
                description = request.POST.getlist('description')
                option_qry_pk = request.POST.getlist('option-qry-pk')
                item_number = int(request.POST.get('total-item-number'))

                if new_ques.form_type == 'card-carousel-form' or new_ques.form_type == 'card-carousel-option-form':
                    for i in description:
                        if not i:
                            data = {
                                'status': False,
                                'message': 'Card Body is required'
                            }
                            return JsonResponse(data)

                if new_ques.form_type == 'image-carousel-form' or new_ques.form_type == 'image-carousel-option-form':
                    if image_count:
                        total_count = len(image_count) + len(images)
                    else:
                        total_count = len(images)
                    if total_count != item_number:
                        data = {
                            'status': False,
                            'message': 'Image field is required'
                        }
                        return JsonResponse(data)

                data = {
                    'status': True,
                    # 'child_id': child_id,
                    'number': number,
                    'single_option': False,
                    'carousel_option': False
                }
                if new_ques.is_option:
                    options = request.POST.getlist('option')
                    for i in options:
                        if not i:
                            data = {
                                'status': False,
                                'message': 'All options are required'
                            }
                            return JsonResponse(data)
                    carousel_option_dict = {}

                for i in range(item_number):

                    if option_qry_pk[i]:
                        chat_n = CarouselChatQuestion.objects.filter(pk=option_qry_pk[i])
                        chat_n.update(text=texts[i], description=description[i])
                        chat_n = chat_n[0]
                    else:
                        chat_n = CarouselChatQuestion.objects.create(chat_title=new_ques, text=texts[i],
                                                                 description=description[i])
                    try:
                        chat_n.image = images[i]
                    except:
                        pass
                    try:
                        chat_n.number = numbers[i]
                    except:
                        pass

                    if new_ques.is_option:
                        chat_n.option = options[i]
                        new_id = str(uuid.uuid4())
                        chat_n.child_id = new_id
                        carousel_option_dict[chat_n.number] = new_id
                    chat_n.save()

                if new_ques.is_option:
                    data['carousel_option'] = True
                    data['carousel_option_dict'] = carousel_option_dict
                return JsonResponse(data)

        else:
            data = {
                'status': False,
                'message': "chat_new_form form error"
            }

            return JsonResponse(data)
    else:
        data = {
            'status': False,
            'message': "Method get"
        }
    return JsonResponse(data)


@login_required(login_url='user_login')
def remove_save_question(request):
    # try:

    question_pk = int(request.GET['question_pk'])
    ques = ChatQuestionNew.objects.get(pk=question_pk)
    chat_title = ques.chat_title
    parent_company_pk = request.user.company.pk
    if parent_company_pk != chat_title.company.parent_company.pk:
        data = {
            'status': 'invalid',
            'message': 'Invalid request'
        }

        return JsonResponse(data)
    number = ques.number
    if number == 1:
        ChatQuestionNew.objects.filter(chat_title=chat_title).delete()
    else:
        ques.delete()
        ChatQuestionNew.objects.filter(Q(chat_title=chat_title) & Q(parent__gte=number)).delete()

    if request.is_ajax():
        maps = ChatQuestionNew.objects.filter(chat_title=chat_title)
        context = {
            'maps': maps,
        }
        html = render_to_string('bot/map_details.html', context=context, request=request)
        data = {
            'status': True,
            'html': html,
        }
    else:
        data = {
            'status': 'invalid',
            'message': 'Invalid request'
        }
    return JsonResponse(data)


@login_required(login_url='user_login')
def change_chat_map_status(request, id):
    question = ChatTitle.objects.get(pk=id)
    company = question.company
    if request.user.role != 'admin' and request.user.company.pk != company.parent_company.pk:
        return render(request, 'bot/check_user.html')

    question.active = False if question.active else True
    question.save()

    return HttpResponseRedirect(reverse('chat_maps', args=(company.pk, company.name)))


def choose_service_provider(request):
    user_lang = request.GET.get('lang')
    pk = request.GET.get('pk')
    data = service_provider_view(pk, user_lang)
    return JsonResponse(data)


def get_slot_list(request):
    pk = request.GET.get('pk')
    date = request.GET.get('date')
    user_lang = request.GET.get('lang')
    data = get_slots(pk, date, user_lang)
    return JsonResponse(data)


def book_selected_slot(request):
    # try:
    slot_pk = request.GET.get('selected_slot')
    date = request.GET.get('selected_date')
    slot_time = request.GET.get('slot_time')
    provider_pk = request.GET.get('selected_provider')
    u_id = request.GET.get('u_id')

    data = book_selected_slot_view(slot_pk, date, slot_time, provider_pk, u_id)

    # except:
    #     data = {
    #         'status': False
    #     }

    return JsonResponse(data)


@login_required(login_url='user_login')
def facebook_detail(request):
    if request.user.role != 'admin':
        return render(request, 'bot/check_user.html')
    parent_company = request.user.company
    companies = Company.objects.filter(parent_company=parent_company)
    for company in companies:
        if not FacebookBotDetails.objects.filter(company=company):
            while True:
                token = random.randint(10000000, 99999999)
                token_exists = FacebookBotDetails.objects.filter(verify_key=token).exists()
                if token_exists:
                    continue
                else:
                    break

            if not FacebookBotDetails.objects.filter(company=company).exists():
                token_instance = FacebookBotDetails.objects.create(company=company, verify_key=token)

    form = FacebookBotDetailForm()
    if request.method == 'POST':
        form = FacebookBotDetailForm(request.POST)
        if form.is_valid():
            company_pk = request.POST['company-pk-input']
            verify_token = request.POST['verify-token-input']
            company = get_object_or_404(Company, pk=company_pk)
            fb_obj = FacebookBotDetails.objects.get(Q(company=company) & Q(verify_key=verify_token))
            fb_obj.access_key = form.cleaned_data['access_key']
            fb_obj.page_id = form.cleaned_data['page_id']
            fb_obj.save()
            return HttpResponseRedirect(reverse('facebook_detail'))

    context = {
        'form': form,
        'facebook_detail': 'active',
        'companies': companies,
    }

    return render(request, 'bot/facebook_detail.html', context)

