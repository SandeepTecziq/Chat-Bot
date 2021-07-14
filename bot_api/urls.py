from django.urls import path
from .views import *


urlpatterns = [
    path('get_user_detail/<secret_key>/', GetUserDetailView.as_view()),
    path('bot_reply/<secret_key>/', BotReplyView.as_view()),
    path('start_chat_map/', StartChatView.as_view()),
    path('service_provider_list/', ServiceProviderView.as_view()),
    path('get_slots/', GetSlotView.as_view()),
    path('book_selected_slot/', BookSelectedSlotView.as_view()),
    path('language_list/', LanguageList.as_view()),
    path('get_colors/', GetColors.as_view()),
    path('start_bot_chat/', StartBotChat.as_view()),
    path('change_language/', ChangeLanguage.as_view()),
    path('after_slot_click/', AfterSlotClick.as_view()),
]