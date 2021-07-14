from django.contrib import admin
from .models import *


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'role')


class ParentCompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'secret_key')


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'parent_company', 'name', 'secret_key', 'bot_name', 'image')


class QuestionTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'tag', 'company')


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_tag', 'question_text')


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_tag', 'question', 'answer_text', 'customer_care')


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'company', 'u_field')


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'customer', 'message', 'read_status', 'time_added', 'note_type')


class EmpNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'customer', 'message', 'read_status', 'time_added')


class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'history', 'question', 'answer', 'time')


class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'date_time', 'company', 'date', 'chat_type', 'talker', 'saved_status', 'customer',
                    'trained_status')


class NotifyAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'number', 'note_type')


class EmpNotifyAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'number')


class ChatTitleAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'title')


class ChatQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'chat_title', 'type', 'number', 'parent', 'options')


class TImeSlotAdmin(admin.ModelAdmin):
    list_display = ('id', 'start', 'end', 'name', 'provider')


class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'company')


class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'slot', 'date')


class FacebookBotDetailsAdmin(admin.ModelAdmin):
    list_display = ('company','verify_key', 'page_id', 'access_key')


class ChatQuestionNewAdmin(admin.ModelAdmin):
    list_display = ('chat_title', 'text', 'is_first', 'is_option', 'carousel_type', 'number', 'parent', 'u_id', 'child_id')


class SingleChatQuestionAdmin(admin.ModelAdmin):
    list_display = ('chat_title', 'image', 'url', 'options')


class CarouselChatQuestionAdmin(admin.ModelAdmin):
    list_display = ('chat_title', 'image', 'option', 'text', 'description', 'number', 'child_id')


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'currency', 'bot_allowed', 'is_default')


class TakenSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'parent_company', 'subscription', 'date', 'paid', 'remaining_bot')


class ActiveBotsAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'bot')


admin.site.register(ActiveBots, ActiveBotsAdmin)
admin.site.register(SubscriptionPlan, SubscriptionAdmin)
admin.site.register(TakenSubscription, TakenSubscriptionAdmin)
admin.site.register(ParentCompany, ParentCompanyAdmin)
admin.site.register(CarouselChatQuestion, CarouselChatQuestionAdmin)
admin.site.register(SingleChatQuestion, SingleChatQuestionAdmin)
admin.site.register(ChatQuestionNew, ChatQuestionNewAdmin)
admin.site.register(FacebookBotDetails, FacebookBotDetailsAdmin)
admin.site.register(TimeSlots, TImeSlotAdmin)
admin.site.register(ServiceProvider, ServiceProviderAdmin)
admin.site.register(BookedSlots, BookingAdmin)
admin.site.register(ChatQuestion, ChatQuestionAdmin)
admin.site.register(ChatTitle, ChatTitleAdmin)
admin.site.register(QuestionTag, QuestionTagAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(EmpNotification, EmpNotificationAdmin)
admin.site.register(ChatHistory, ChatHistoryAdmin)
admin.site.register(Conversation, ConversationAdmin)
admin.site.register(NotifyNumber, NotifyAdmin)
admin.site.register(EmpNotifyNumber, EmpNotifyAdmin)