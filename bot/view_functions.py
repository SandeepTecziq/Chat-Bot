from .models import Company, Question, ParentCompany, NotifyNumber, Notification, BookedSlots
from django.db.models import Q
from django.core.mail import send_mail
from .email_messages import *


def send_mail_function(subject, message, to_email):
    send_mail(subject, message, 'donotreply@vanloc.fr', to_email, fail_silently=False, )


def get_all_detail(secret_key):
    company = ParentCompany.objects.get(secret_key=secret_key)
    note_number = NotifyNumber.objects.filter(company__parent_company=company)
    no_num = note_number.filter(note_type='note_no')
    yes_num = note_number.filter(note_type='note_yes')
    note_no_num = no_num[0].number if no_num else 0
    note_yes_num = yes_num[0].number if yes_num else 0
    note_number = (note_no_num, note_yes_num)
    notification = Notification.objects.filter(company__parent_company=company)
    employees = company.company_name.filter(role='employee')

    return company, note_number, notification, employees


def check_trained_status(secret_key):
    if_trained = Question.objects.filter(Q(question_tag__company__secret_key=secret_key) & Q(if_trained=False)).exists()

    return if_trained


def send_booking_confirmation_mail(user_email, user_name, owner_name, owner_email, slot_pk):
    slot = BookedSlots.objects.filter(pk=slot_pk).first()
    if slot:
        start_time = slot.slot.start
        end_time = slot.slot.end
        provider = slot.slot.provider.name
        company = slot.slot.provider.company.name
        category = slot.slot.provider.category.name if slot.slot.provider.category else "-"

        user_msg = book_slot_user_msg.format(**{'user_name': user_name, 'start_time': start_time, 'end_time': end_time,
                                              'provider': provider, 'slot_date': slot.date})
        owner_msg = book_slot_owner_msg.format(**{'user_name': user_name, 'start_time': start_time, 'end_time': end_time,
                                              'provider': provider, 'owner_name': owner_name, 'slot_date': slot.date,
                                               'user_email': user_email, 'company': company})
        subject = 'New booking confirmed'
        send_mail_function(subject, user_msg, [user_email])
        send_mail_function(subject, owner_msg, [owner_email])

    else:
        pass

