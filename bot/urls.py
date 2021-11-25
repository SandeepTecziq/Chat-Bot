from django.urls import path

from . import views, fb_views, views2

urlpatterns = [
    path('', views.index, name='index'),
    path('pricing', views.pricing, name='pricing'),
    path('templates', views.templates, name='templates'),
    path('solutions', views.solutions, name='solutions'),
    path('chat/<secret_key>/<lang>/<u_id>/', views.room, name='room'),
    path('chat_customer/<secret_key>/<u_id>/<ques>/', views.room_customer, name='room_customer'),
    path('create_file', views.create_file, name='create_file'),
    path('notify/<id>/<slug>/', views.add_question, name='notify'),
    path('question_list/', views.question_list, name='question_list'),
    path('question_detail/', views.question_detail, name='question_detail'),
    path('chat_history', views.chat_history, name='chat_history'),
    path('get_conversation/<secret_key>/<id>/', views.get_conversation, name='get_conversation'),
    path('remove_note', views.remove_note, name='remove_note'),
    path('remove_emp_notification', views.remove_emp_notification, name='remove_emp_notification'),
    path('change_read_status_note', views.change_read_status_note, name='change_read_status_note'),
    path('change_emp_read_status_note', views.change_emp_read_status_note, name='change_emp_read_status_note'),
    path('login', views.user_login, name='user_login'),
    path('logout', views.user_logout, name='user_logout'),
    path('employee_page/<secret_key>/', views.employee_page, name='employee_page'),
    path('create_user/', views.create_user, name='create_user'),
    path('save_chat_customer', views.save_chat_customer, name='save_chat_customer'),
    path('train_chat_data', views.train_chat_data, name='train_chat_data'),
    path('create_chat_map/<pk>/<bot_slug>/', views.create_chat_map, name='create_chat_map'),
    path('get_user_detail/<secret_key>/', views.get_user_detail, name='get_user_detail'),
    path('update_bot_detail/<pk>/<slug>', views.update_bot_detail, name='update_bot_detail'),
    path('chat_maps/<pk>/<slug>/', views.chat_maps, name='chat_maps'),
    path('bot_list/', views.bot_list, name='bot_list'),
    path('add_bot/', views.add_bot, name='add_bot'),
    path('add_bot_to_user/', views.add_bot_to_user, name='add_bot_to_user'),
    path('delete_chat_title/<id>/', views.delete_chat_title, name='delete_chat_title'),
    path('create_time_slot/', views.create_time_slot, name='create_time_slot'),
    path('provider_detail/', views.provider_detail, name='provider_detail'),
    path('create_service_provider/', views.create_service_provider, name='create_service_provider'),
    path('change_provider_state', views.change_provider_state, name='change_provider_state'),
    path('change_password', views.change_password, name='change_password'),
    path('company_list', views.company_list, name='company_list'),
    path('forget_password', views.forget_password, name='forget_password'),
    path('choose_service_provider/', views.choose_service_provider, name='choose_service_provider'),
    path('integration/', views.facebook_detail, name='facebook_detail'),
    path('change_chat_map_status/<id>', views.change_chat_map_status, name='change_chat_map_status'),
    path('get_slot_list', views.get_slot_list, name='get_slot_list'),
    path('intro_change_language', views.intro_change_language, name='intro_change_language'),
    path('78265fc81d199e51016ef810f1d355e5ea7bef7f682b855d94', fb_views.fb_chat_view, name='fb_chat_view'),
    path('room_test/<pk>/<lang>/', fb_views.room_test, name='room_test'),
    path('create_subscription_plan/', fb_views.create_subscription_plan, name='create_subscription_plan'),
    path('activate_bot/<id>/<secret_key>/', fb_views.activate_bot, name='activate_bot'),
    path('process_payment/<subscription_id>/<subscription_type>', fb_views.process_payment, name='process_payment'),
    path('process-payment/', fb_views.process_payment, name='process_payment'),
    path('payment-done/', fb_views.payment_done, name='payment_done'),
    path('payment-cancelled/', fb_views.payment_canceled, name='payment_cancelled'),
    path('activate_user/<user_pk>', fb_views.activate_user, name='activate_user'),
    path('subscription_list/', fb_views.subscription_list, name='subscription_list'),
    path('faq_page/', fb_views.faq_page, name='faq_page'),
    path('check_ml_status/', fb_views.check_ml_status, name='check_ml_status'),
    path('activate_subscription_plan/<pk>', fb_views.activate_subscription_plan, name='activate_subscription_plan'),
    path('delete_subscription_plan/<pk>', fb_views.delete_subscription_plan, name='delete_subscription_plan'),
    path('get_bot_reply_updated/', views2.get_bot_reply_updated, name='get_bot_reply_updated'),
    path('chat_map_questions/<pk>/<slug>/', views2.chat_map_questions, name='chat_map_questions'),
    path('save_chat_questions/<pk>/<slug>/', views2.save_chat_questions, name='save_chat_questions'),
    path('edit_chat_questions/<pk>/', views2.edit_chat_questions, name='edit_chat_questions'),
    path('remove_save_question/<title_pk>/<question_pk>/', views2.remove_save_question, name='remove_save_question'),
    path('sort_title_questions/<title_pk>/', views2.sort_title_questions, name='sort_title_questions'),
    path('bot_testing/<secret_key>/<lang>/', views2.bot_testing, name='bot_testing'),
    path('get_next_question/<title_pk>/<question_pk>/<is_option>/', views2.get_next_question, name='get_next_question'),
    path('book_selected_slot', views2.book_selected_slot, name='book_selected_slot'),
    path('get_provider_category', views2.get_provider_category, name='get_provider_category'),
    path('get_available_employees/<company_pk>', views2.get_available_employees, name='get_available_employees'),
]
