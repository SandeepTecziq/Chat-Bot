from .models import Company, Question, ParentCompany, NotifyNumber, Notification
from django.db.models import Q


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
