from django.shortcuts import HttpResponse, get_object_or_404, render, HttpResponseRedirect
from django.urls import reverse
import json
import datetime
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
import requests
from bot.models import FacebookBotDetails, User, Company, SubscriptionPlan, TakenSubscription, ParentCompany, ActiveBots, Question, TimeSlots
from googletrans import Translator
from .chatgui import bot_reply
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .forms2 import CreateSubscriptionForm
from django.conf import settings
from decimal import Decimal
from paypal.standard.forms import PayPalPaymentsForm


@csrf_exempt
def fb_chat_view(request):
    fb_details = FacebookBotDetails.objects.all()
    if request.method == 'GET':
        for i in fb_details:
            if request.GET['hub.verify_token'] == i.verify_key:
                return HttpResponse(request.GET['hub.challenge'])

        return HttpResponse('Error, invalid token')

    incoming_message = json.loads(request.body.decode('utf-8'))
    for entry in incoming_message['entry']:
        for message in entry['messaging']:
            if 'message' in message:
                text = message['message']['text']
                recipient = message['recipient']['id']
                bot_qry = fb_details.filter(page_id=recipient)[0]
                company = bot_qry.company
                company_name = company.name[10] if len(company.name) > 10 else company.name
                dir_name = 'company_files/' + str(company.id) + '_' + company_name + '/'
                token = bot_qry.access_key
                reply = bot_reply(text, dir_name)
                post_facebook_message(message['sender']['id'], reply, token)
    return HttpResponse("g")


def post_facebook_message(fbid, recevied_message, token):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=' + token
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":recevied_message}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)


def room_test(request, pk, lang):
    try:
        translate = Translator()
        company = get_object_or_404(Company, pk=pk)
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
            'secret_key': company.secret_key,
            'company': company,
            'dir_name': dir_name,
            'lang': lang,
            'translated_dict': translated_dict,
            'chat_titles': chat_titles,
            'static_dict': static_dict,
        }
        return render(request, 'question-template/room_test.html', context)
    except:
        return render(request, 'bot/404_page.html')


def get_bot_reply(request):
    question = request.GET.get('question', None)
    dir_name = request.GET.get('dir_name', None)
    try:
        reply = bot_reply(question, dir_name)
    except:
        reply = 'System can not answer this question. Would you like to talk to our customer care service.'

    if reply == 'System can not answer this question. Would you like to talk to our customer care service.':
        get_answer = 'fail'
    else:
        get_answer = 'pass'

    data = {
        'status': True,
        'reply': reply,
        'get_answer': get_answer,
    }

    return JsonResponse(data)


@login_required(login_url='user_login')
def activate_bot(request, id, secret_key):
    bot = Company.objects.filter(Q(pk=id) & Q(secret_key=secret_key))
    if request.user.role != 'admin' and request.user.company.pk != bot.parent_company.pk:
        return render(request, 'bot/check_user.html')

    if secret_key:
        bot = bot[0]
        if bot.active:
            bot.active = False
            number = bot.active_bot.subscription.remaining_bot + 1
            TakenSubscription.objects.filter(active_bot__bot=bot).update(remaining_bot=number)
            ActiveBots.objects.filter(bot=bot).delete()
        else:
            plan = TakenSubscription.objects.filter(Q(parent_company=bot.parent_company) & Q(paid=True) & Q(remaining_bot__gt=0))
            if plan:
                plan = plan[0]
                number = plan.remaining_bot - 1
                plan.remaining_bot = number
                plan.save()
                bot.active_date = datetime.datetime.now()
                bot.active = True
                ActiveBots.objects.create(subscription=plan, bot=bot)
            else:
                return HttpResponseRedirect(reverse('bot_list'))
        bot.save()
        return HttpResponseRedirect(reverse('bot_list'))
    else:
        return HttpResponseRedirect(reverse('bot_list'))


@login_required(login_url='user_login')
def create_subscription_plan(request):
    if request.user.is_staff == False or request.user.is_superuser == False:
        return render(request, 'bot/check_user.html')

    plans = SubscriptionPlan.objects.all()

    form = CreateSubscriptionForm()
    if request.method == 'POST':
        form = CreateSubscriptionForm(request.POST)
        form.save()
        return HttpResponseRedirect(reverse('create_subscription_plan'))

    context = {
        'form': form,
        'plans': plans,
    }

    return render(request, 'question-template/create_subscription_plan.html', context)


@login_required(login_url='user_login')
def process_payment(request, subscription_id, subscription_type):
    if request.user.role != 'admin':
        return render(request, 'bot/check_user.html')

    subscription = get_object_or_404(SubscriptionPlan, u_id=subscription_id)
    parent_company = request.user.company

    if subscription_type == 'monthly':
        price = subscription.price
        expire_date = datetime.datetime.now() + timedelta(days=30)
    elif subscription_type == 'yearly':
        price = 12*(subscription.price - subscription.price/10)
        expire_date = datetime.datetime.now() + timedelta(days=365)
    else:
        return HttpResponseRedirect(reverse('subscription_list'))

    taken_subscription = TakenSubscription.objects.create(subscription=subscription, parent_company=parent_company,
                                                          expire_date=expire_date, remaining_bot=subscription.bot_allowed)
    invoice = taken_subscription.invoice

    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': price,
        'item_name': subscription.name,
        'invoice': str(invoice),
        'currency_code': subscription.currency,
        'notify_url': request.build_absolute_uri(reverse('paypal-ipn')),
        'return_url': request.build_absolute_uri(reverse('payment_done')),
        'cancel_return': request.build_absolute_uri(reverse('payment_cancelled')),
    }

    form = PayPalPaymentsForm(initial=paypal_dict)

    context = {
        'form': form,
        'subscription': subscription,
        'price': price,
        'subscription_type': subscription_type,
    }
    return render(request, 'question-template/process_payment.html', context)


@csrf_exempt
def payment_done(request):
    return HttpResponseRedirect(reverse('bot_list'))


@csrf_exempt
def payment_canceled(request):
    return render(request, 'question-template/payment_cancelled.html')


@login_required(login_url='user_login')
def activate_user(request, user_pk):
    user = get_object_or_404(User, pk=user_pk)
    if request.user.role != 'admin' and user.company.pk != request.user.company.pk and user.role != 'employee':
        return render(request, 'bot/check_user.html')

    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True
    user.save()

    return HttpResponseRedirect(reverse('create_user'))


@login_required(login_url='user_login')
def subscription_list(request):
    if request.user.role != 'admin':
        return render(request, 'bot/check_user.html')
    plans = SubscriptionPlan.objects.filter(is_active=True)[:3]
    context = {
        'subscription_list': 'active',
        'plans': plans,
    }
    return render(request, 'question-template/subscription_list.html', context)


@login_required(login_url='user_login')
def faq_page(request):
    context = {
        'faq_page': 'active',
    }
    return render(request, 'question-template/faq_page.html', context)


@login_required(login_url='user_login')
def activate_subscription_plan(request, pk):
    if request.user.is_staff == False or request.user.is_superuser == False:
        return render(request, 'bot/check_user.html')

    plan = get_object_or_404(SubscriptionPlan, pk=pk)

    if plan.is_active:
        plan.is_active = False
    else:
        plan.is_active = True
    plan.save()

    return HttpResponseRedirect(reverse('create_subscription_plan'))


@login_required(login_url='user_login')
def delete_subscription_plan(request, pk):
    if request.user.is_staff == False or request.user.is_superuser == False:
        return render(request, 'bot/check_user.html')

    plan = SubscriptionPlan.objects.filter(pk=pk)
    plan.delete()
    return HttpResponseRedirect(reverse('create_subscription_plan'))


@login_required(login_url='user_login')
def check_ml_status(request):
    key = request.GET.get('secret_key')
    company = Company.objects.filter(secret_key=key)
    if company:
        company = company[0]
        question = Question.objects.filter(Q(question_tag__company=company) & Q(if_trained=True)).exists()
        ml_status = True if question else False
        slot = TimeSlots.objects.filter(provider__company=company).exists()
        slot_status = True if slot else False


        data = {
            'status': True,
            'ml_status': ml_status,
            'slot_status': slot_status,
        }
    else:
        data = {
            'status': False
        }
    return JsonResponse(data)
