from googletrans import Translator
from bot.models import ChatTitle, ServiceProvider, Company, TimeSlots, BookedSlots, Customer
from django.db.models import Q, Prefetch
import datetime
from django.core.mail import send_mail, EmailMessage


def service_provider_view(pk, user_lang, date):
    # try:
    company = Company.objects.filter(pk=pk).first()
    if not company:
        data = {
            'status': False,
            'message': 'No company found with provided secret key'
        }

        return data
    booked_slots = BookedSlots.objects.filter(date=date).values_list('slot')
    providers = ServiceProvider.objects.filter(Q(company=company) & Q(provider_slot__isnull=False)).prefetch_related(
        Prefetch('provider_slot', queryset=TimeSlots.objects.exclude(pk__in=booked_slots), to_attr='available_slots')).distinct()

    if not providers:
        data = {
            'status': False,
            'message': 'No service provider found for this bot.'
        }

        return data

    company_lang = company.language
    provider_list = []
    service_provider = company.service_provider
    service_provider_line = "Please select " + service_provider + " and slot or click the icon to select date again"
    for i in providers:

        ls = []
        for j in i.available_slots:
            ls.append({'pk': j.pk, 'from': j.start, 'to': j.end, 'days': j.days['day']})
        provider_element = {'pk': i.pk, 'name': i.name, 'slots': ls}
        provider_list.append(provider_element)
    if user_lang != company_lang:
        translate = Translator()
        service_provider_line = translate.translate(service_provider_line, src=company_lang, dest=user_lang).text

    data = {
        'status': True,
        'providers': provider_list,
        'service_provider_line': service_provider_line,
        'date': date,
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
