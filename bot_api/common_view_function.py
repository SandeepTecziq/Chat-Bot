from googletrans import Translator
from bot.models import ChatTitle, ChatQuestionNew, ServiceProvider, Company, TimeSlots, BookedSlots, Customer, ChatQuestion
from django.db.models import Q
import datetime
from django.core.mail import send_mail, EmailMessage


def get_title_pk(main_type, title_pk, option_number, number):
    title_qry = ChatTitle.objects.filter(pk=title_pk)
    if title_qry:
        title_qry = title_qry[0]
    else:
        data = {
            'status': False,
            'message': 'Incorrect Title PK'
        }
        return data
    if main_type == 'start':
        chat_title = ChatQuestionNew.objects.filter(Q(chat_title=title_qry) & Q(number=1))
        if not chat_title:
            data = {
                'status': False,
                'message': 'Chatmap does not exists.'
            }
            return data
        else:
            chat_title = chat_title[0]

    elif main_type == 'next':

        if option_number == 'false':
            chat_title = ChatQuestionNew.objects.filter(Q(chat_title=title_qry) & Q(parent=number))
            if chat_title:
                chat_title = chat_title[0]

            else:
                data = {
                    'status': 'end_chat',
                }
                return data
        else:
            chat_title_option = ChatQuestionNew.objects.filter(Q(chat_title=title_qry) & Q(parent=option_number))
            chat_title_text = ChatQuestionNew.objects.filter(Q(chat_title=title_qry) & Q(parent=number))
            if chat_title_option:
                chat_title = chat_title_option[0]

            elif chat_title_text:
                chat_title = chat_title_text[0]

            else:
                data = {
                    'status': 'end_chat',
                }
                return data

    else:
        data = {
            'status': False,
            'message': 'Invalid main type.'
        }
        return data

    data = {
        'status': True,
        'title_pk': chat_title.pk
    }
    return data


def start_chat_view(title_pk, user_lang):

    chat_title = ChatQuestionNew.objects.get(pk=title_pk)
    company_lang = chat_title.chat_title.company.language
    if user_lang == company_lang:
        question = chat_title.text
    else:
        translate = Translator()
        question = translate.translate(chat_title.text, src=company_lang, dest=user_lang).text

    data = {
        'company_pk': chat_title.chat_title.company.pk,
        'title_pk': chat_title.chat_title.pk,
        'question': question,
        'pk': chat_title.pk,
        'number': chat_title.number,
        'status': True,
        'child_id': chat_title.child_id,
        'carousel_type': chat_title.carousel_type,
        'form_type': chat_title.form_type,
        'detail': {},
        'is_option': chat_title.is_option,
    }
    if chat_title.carousel_type == 'single':
        detail = {}
        if chat_title.single_chat_question.image:
            detail['image'] = chat_title.single_chat_question.image.url
        else:
            detail['image'] = False
        detail['url'] = chat_title.single_chat_question.url
        if user_lang == company_lang:
            detail['text'] = chat_title.single_chat_question.single_text
            detail['options'] = chat_title.single_chat_question.options
            detail['description'] = chat_title.single_chat_question.description
        else:
            translate = Translator()
            text = translate.translate(chat_title.single_chat_question.single_text, src=company_lang, dest=user_lang).text
            desc = translate.translate(chat_title.single_chat_question.description, src=company_lang, dest=user_lang).text
            if chat_title.options:
                options = chat_title.options
                for i, j in options.items():
                    options[i][0] = translate.translate(j[0], src=company_lang, dest=user_lang).text

            else:
                options = {}
            detail['options'] = options
            detail['text'] = text
            detail['description'] = desc

    elif chat_title.carousel_type == 'carousel':
        detail = []
        for frame in chat_title.carousel_chat_question.all():
            frame_detail = {}

            frame_detail['number'] = frame.number
            frame_detail['child_id'] = frame.child_id
            if frame.image:
                frame_detail['image'] = frame.image.url
            else:
                frame_detail['image'] = ''

            if user_lang == company_lang:
                frame_detail['option'] = frame.option
                frame_detail['text'] = frame.text
                frame_detail['description'] = frame.description
            else:
                option = translate.translate(frame.option, src=company_lang, dest=user_lang).text
                text = translate.translate(frame.text, src=company_lang, dest=user_lang).text
                description = translate.translate(frame.description, src=company_lang, dest=user_lang).text
                frame_detail['option'] = option
                frame_detail['text'] = text
                frame_detail['description'] = description

            detail.append(frame_detail)

    data['detail'] = detail

    return data


def next_question_view(number, pk, user_lang):
    curr_ques = ChatQuestion.objects.get(pk=pk)
    chat_name = ChatTitle.objects.get(chat_question__pk=pk)
    ques = ChatQuestion.objects.filter(Q(chat_title=chat_name) & Q(parent=number))
    ques_1 = ChatQuestion.objects.filter(Q(chat_title=chat_name) & Q(parent=curr_ques.number))
    company_lang = chat_name.company.language
    book_appointment = False
    book_id = 0

    if ques:
        next_ques = ques
    else:
        next_ques = ques_1

    if next_ques:
        if next_ques[0].question == 'Do you want to book appointment?':
            book_appointment = True
            for i, j in next_ques[0].options.items():
                if j == 'Yes':
                    book_id = i

        if user_lang == company_lang:
            question = next_ques[0].question
            if next_ques[0].options:
                options = next_ques[0].options
            else:
                options = {}
        else:
            translate = Translator()
            question = translate.translate(next_ques[0].question, src=company_lang, dest=user_lang).text
            if next_ques[0].options:
                options = {}
                for i, j in next_ques[0].options.items():
                    opt = translate.translate(j, src=company_lang, dest=user_lang).text
                    options[i] = opt
            else:
                options = {}
        data = {
            'found': True,
            'question': question,
            'type': next_ques[0].type,
            'options': options,
            'pk': next_ques[0].pk,
            'number': next_ques[0].number,
            'book_appointment': book_appointment,
            'book_id': book_id,
        }
        if next_ques[0].images:
            data['images'] = next_ques[0].images.url
        else:
            data['images'] = False
        return data

    else:
        data = {
            'found': False,
        }
        return data


def service_provider_view(pk, user_lang):
    # try:
    company = Company.objects.filter(pk=pk)
    if not company:
        data = {
            'status': False,
            'message': 'No company found with provided secret key'
        }

        return data

    else:
        company = company[0]
    providers = ServiceProvider.objects.filter(Q(company=company) & Q(provider_slot__isnull=False))

    if not providers:
        data = {
            'status': False,
            'message': 'No service provider found for this bot.'
        }

        return data

    company_lang = company.language
    provider_list = {}
    calender_line = "Click on calender icon to open calender."
    if user_lang == company_lang:
        service_provider = company.service_provider
        service_provider_line = "Please select"

        for i in providers:
            provider_list[i.pk] = i.name

    else:

        translate = Translator()
        service_provider = translate.translate(company.service_provider, src=company_lang, dest=user_lang).text
        service_provider_line = translate.translate('Please select', src='en', dest=user_lang).text
        calender_line = translate.translate(calender_line, src='en', dest=user_lang).text
        for i in providers:
            provider_list[i.pk] = translate.translate(i.name, src=company_lang, dest=user_lang).text

    data = {
        'status': True,
        'providers': provider_list,
        'service_provider': service_provider,
        'service_provider_line': service_provider_line,
        'calender_line': calender_line,
    }

    # except:
    #     data = {
    #         'status': False,
    #         'message': 'Something went wrong. Please refresh and try again. not sandeep'
    #     }
    return data


def get_slots(pk, date, user_lang):
    translate = Translator()
    slots = TimeSlots.objects.filter(provider__pk=pk)
    print(slots)
    slot_dict = {}
    for i in slots:
        book = BookedSlots.objects.filter(Q(date=date) & Q(slot__pk=i.pk)).exists()
        if not book:
            start = datetime.datetime.strptime(str(i.start), "%H:%M:%S")
            end = datetime.datetime.strptime(str(i.end), "%H:%M:%S")
            slot_dict[i.pk] = str(start.strftime("%I:%M %p")) + ' - ' + str(end.strftime("%I:%M %p"))
    if len(slot_dict) == 0:
        try:
            msg = translate.translate('No slot available on given date. Please select a another date', src='en', dest=user_lang).text
        except:
            try:
                msg = translate.translate('No slot available on given date. Please select a another date', src='en',
                                          dest=user_lang).text
            except:
                msg = "Something went wrong. Please try after 5 sec"

        data = {
            'status': False,
            'message': msg,
        }

        return data
    t_line = 'Please select a slot:'
    try:
        get_slot_line = translate.translate(t_line, src='en', dest=user_lang).text
        data = {
            'status': True,
            'slots': slot_dict,
            'get_slot_line': get_slot_line,
        }
    except:
        try:
            get_slot_line = translate.translate(t_line, src='en', dest=user_lang).text
            data = {
                'status': True,
                'slots': slot_dict,
                'get_slot_line': get_slot_line,
            }
        except:
            data = {
                'status': False,
                'message': "Something went wrong. Please try after 5 sec",
            }

    return data


def book_selected_slot_view(slot_pk, date, slot_time, provider_pk, u_id):
    # try:
    provider = ServiceProvider.objects.get(pk=provider_pk).name

    slot = TimeSlots.objects.get(pk=slot_pk)
    BookedSlots.objects.create(slot=slot, date=date)

    user = Customer.objects.get(u_field=u_id)
    user_email = user.email
    user_name = user.name
    admin_email = user.company.parent_company.company_name.all()[0].email
    subject = "Appointment booking confirmation"
    variable_dict = {'user_name': user_name, 'provider': provider, 'date': date, 'slot': slot_time}
    mail_message = '''
            Appointment has been booked for {user_name}. Following are the details:
                Service Provider: {provider},
                Date: {date},
                Slot: {slot}
            '''.format(**variable_dict)
    send_mail(
        subject,
        mail_message,
        'skeshari@tecziq.com',
        [user_email, admin_email],
        fail_silently=False,
    )
    # msg = EmailMessage(subject, mail_message, to=[user_email, admin_email])
    # msg.send()

    data = {
        'status': True
    }

    return data
    # except:
    #     data = {
    #         'status': False
    #     }
    #
    #     return data
