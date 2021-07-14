from django.db import models
from jsonfield import JSONField
from django.contrib.auth.models import AbstractUser
import uuid
import googletrans


LANGUAGES = ((i, j) for i,j in googletrans.LANGUAGES.items())


def company_image_upload_path(instance, filename):
    return "{company_name}/company_image/{file}".format(company_name=instance.name, file=filename)


def company_question_upload_path(instance, filename):
    return "{company_name}/question_image/{file}".format(company_name=instance.chat_title.chat_title.company.name, file=filename)


class ParentCompany(models.Model):
    name = models.CharField(max_length=30)
    secret_key = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.name


class Company(models.Model):
    parent_company = models.ForeignKey(ParentCompany, on_delete=models.CASCADE, related_name='companies', null=True)
    name = models.CharField(max_length=30)
    secret_key = models.UUIDField(default=uuid.uuid4, editable=False)
    bot_name = models.CharField(max_length=30, default='Talking Bot')
    image = models.ImageField(null=True, blank=True, upload_to=company_image_upload_path)
    color = models.CharField(max_length=10, default='#76b61b')
    intro_ques = models.CharField(max_length=255, default='What help do you need')
    bot_ques = models.CharField(max_length=255, default='Hi! you can ask anything')
    bot_title = models.CharField(max_length=30, default='Talk to bot')
    head_text_color = models.CharField(max_length=10, default='#ffffff')
    intro_text_login = models.CharField(max_length=300, default='Please fill form to continue.')
    service_provider = models.CharField(max_length=20, default='service provider')
    language = models.CharField(max_length=15, choices=LANGUAGES, default='en')
    active = models.BooleanField(default=False)
    provider_line = models.CharField(max_length=500, default='Please select the service provider')
    slot_line = models.CharField(max_length=500, default='Please select the slot')
    active_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.name


class FacebookBotDetails(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='facebook_bot')
    access_key = models.CharField(max_length=255, null=True, blank=True)
    verify_key = models.CharField(max_length=8, unique=True)
    page_id = models.CharField(max_length=30, null=True, blank=True, unique=True)


class User(AbstractUser):
    ROLE = (
        ('admin', 'admin'),
        ('employee', 'employee')
    )
    company = models.ForeignKey(ParentCompany, on_delete=models.CASCADE, related_name='company_name', null=True)
    role = models.CharField(max_length=10, choices=ROLE, default='admin')
    bots = models.ManyToManyField(Company, related_name='users', blank=True)

    def __str__(self):
        return self.username


class QuestionTag(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE,
                                related_name='company_tag', default='1')
    tag = models.TextField()


class Question(models.Model):
    question_tag = models.OneToOneField(QuestionTag, on_delete=models.CASCADE,
                                     related_name='question_tag_name')
    question_text = JSONField()
    if_trained = models.BooleanField(default=False)


class Answer(models.Model):
    question_tag = models.OneToOneField(QuestionTag, on_delete=models.CASCADE,
                                     related_name='answer_tag_name')
    question = models.OneToOneField(Question, on_delete=models.CASCADE,
                                 related_name='question_name')
    answer_text = models.TextField()
    customer_care = models.ForeignKey(User, on_delete=models.SET_NULL,
                                      related_name='user_name', null=True)


class Customer(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_customer')
    name = models.CharField(max_length=30)
    email = models.EmailField()
    u_field = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.name


class Notification(models.Model):
    TYPE = (
        ('note_no', 'note_no'),
        ('note_yes', 'note_yes'),
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='cust_notify')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='comp_notify')
    message = models.TextField()
    read_status = models.BooleanField(default=False)
    time_added = models.DateTimeField(auto_now_add=True)
    note_type = models.CharField(max_length=30, choices=TYPE)


class ChatHistory(models.Model):
    TYPE = (
        ('bot_chat', 'bot_chat'),
        ('user_chat', 'user_chat')
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_chat')
    conversation = JSONField(default={'a': 'a'})
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, related_name='customer_chat')
    date_time = models.DateTimeField(auto_now_add=True)
    date = models.DateField(auto_now_add=True)
    chat_type = models.CharField(max_length=10, choices=TYPE)
    talker = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='user_chat', null=True)
    saved_status = models.BooleanField(default=False)
    trained_status = models.BooleanField(default=True)

    class Meta:
        ordering = ['-pk']


class Conversation(models.Model):
    history = models.ForeignKey(ChatHistory, on_delete=models.CASCADE, related_name='chat_history')
    question = models.TextField(null=True)
    answer = models.TextField(null=True)
    time = models.TimeField(auto_now_add=True)


class NotifyNumber(models.Model):
    TYPE = (
        ('note_no', 'note_no'),
        ('note_yes', 'note_yes'),
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_not_number')
    number = models.IntegerField(default=0)
    note_type = models.CharField(max_length=30, choices=TYPE)


class EmpNotification(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='cust_emp_notify')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_emp_notify')
    message = models.TextField()
    read_status = models.BooleanField(default=False)
    time_added = models.DateTimeField(auto_now_add=True)


class EmpNotifyNumber(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_not_number')
    number = models.IntegerField(default=0)


class ChatTitle(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_chat_title')
    title = models.CharField(max_length=50)
    active = models.BooleanField(default=False)

    class Meta:
        unique_together = ('company', 'title')

    def __str__(self):
        return self.title


class ChatQuestion(models.Model):
    TYPE = (
        ('text', 'text'),
        ('option', 'option')
    )
    type = models.CharField(max_length=10, choices=TYPE)
    chat_title = models.ForeignKey(ChatTitle, on_delete=models.CASCADE, related_name='chat_question')
    question = models.CharField(max_length=256)
    number = models.IntegerField()
    parent = models.IntegerField(null=True, blank=True)
    options = JSONField(null=True, blank=True)
    images = models.ImageField(null=True, blank=True)
    is_new = models.BooleanField(default=False)


class ChatQuestionNew(models.Model):
    TYPE = (
        ('single', 'single'),
        ('carousel', 'carousel')
    )
    FORMS = (
        ('text-form', 'text-form'),
        ('card-form', 'card-form'),
        ('text-option-form', 'text-option-form'),
        ('card-option-form', 'card-option-form'),
        ('image-carousel-form', 'image-carousel-form'),
        ('card-carousel-form', 'card-carousel-form'),
        ('image-carousel-option-form', 'image-carousel-option-form'),
        ('card-carousel-option-form', 'card-carousel-option-form'),
    )
    chat_title = models.ForeignKey(ChatTitle, on_delete=models.CASCADE, related_name='question_titles')
    is_first = models.BooleanField(default=False)
    is_option = models.BooleanField(default=False)
    u_id = models.UUIDField(editable=False, null=True)
    child_id = models.UUIDField(default=uuid.uuid4, editable=False)
    carousel_type = models.CharField(max_length=10, choices=TYPE)
    number = models.CharField(max_length=3)
    parent = models.CharField(max_length=3)
    is_new = models.BooleanField(default=True)
    text = models.CharField(max_length=255)
    form_type = models.CharField(max_length=50, choices=FORMS)

    def __str__(self):
        return self.chat_title.title


class SingleChatQuestion(models.Model):
    chat_title = models.OneToOneField(ChatQuestionNew, on_delete=models.CASCADE, related_name='single_chat_question')
    image = models.ImageField(upload_to=company_question_upload_path, null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    options = JSONField(null=True, blank=True)
    single_text = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)


class CarouselChatQuestion(models.Model):
    chat_title = models.ForeignKey(ChatQuestionNew, on_delete=models.CASCADE, related_name='carousel_chat_question')
    image = models.ImageField(upload_to=company_question_upload_path, null=True, blank=True)
    child_id = models.UUIDField(editable=False, null=True, blank=True)
    option = models.CharField(max_length=50, null=True, blank=True)
    text = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    number = models.CharField(max_length=3, null=True, blank=True)


class ServiceProvider(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='user_provider')
    name = models.CharField(max_length=50)
    company = models.ForeignKey(Company, related_name='company_provider', null=True, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class TimeSlots(models.Model):
    start = models.TimeField()
    end = models.TimeField()
    name = models.CharField(max_length=30, null=True, blank=True)
    day = JSONField(default={"day": "All"})
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='provider_slot')

    def __str__(self):
        return self.provider.name + ': ' + str(self.start) + ' - ' + str(self.end)


class BookedSlots(models.Model):
    date = models.DateField()
    slot = models.ForeignKey(TimeSlots, on_delete=models.CASCADE, related_name='booked_slot')


class SubscriptionPlan(models.Model):
    price = models.FloatField()
    bot_allowed = models.IntegerField()
    currency = models.CharField(max_length=5, default='USD')
    name = models.CharField(max_length=30)
    is_default = models.BooleanField(default=False)
    u_id = models.UUIDField(default=uuid.uuid4, editable=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class TakenSubscription(models.Model):
    invoice = models.UUIDField(default=uuid.uuid4, editable=False)
    parent_company = models.ForeignKey(ParentCompany, on_delete=models.CASCADE, related_name='subscription')
    subscription = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name='subscription')
    date = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    expire_date = models.DateTimeField()
    remaining_bot = models.IntegerField(default=1)


class ActiveBots(models.Model):
    subscription = models.ForeignKey(TakenSubscription, related_name='active_bot', on_delete=models.CASCADE)
    bot = models.OneToOneField(Company, related_name='active_bot', on_delete=models.CASCADE)

