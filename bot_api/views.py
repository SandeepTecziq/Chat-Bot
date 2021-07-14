from rest_framework.response import Response
from .serializers import *
from bot.models import *
from bot.models import Company as CompanyModel
from rest_framework.views import APIView
from .view_functions import serializer_error
from .permissions import Check_API_KEY_Auth
from googletrans import Translator
from bot.chatgui import bot_reply
from .common_view_function import *
from django.shortcuts import get_object_or_404


class GetUserDetailView(APIView):
    permission_classes = (Check_API_KEY_Auth,)

    def post(self, request, *args, **kwargs):
        company = CompanyModel.objects.filter(secret_key=kwargs['secret_key'])
        if not company:
            response = {'status': False, 'message': 'Incorrect secret key in url.'}
            return Response(response)
        else:
            company = company[0]

        serializer = GetUserDetailSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer['name'].value
            email = serializer['email'].value
            language = serializer['language'].value

            customer, created = Customer.objects.get_or_create(
                email=email,
                company=company,
                defaults={'name': name}
            )

            u_id = customer.u_field

            # set saved_status to True for this customer previous History

            qry_filter = Q(saved_status=False) & Q(customer=customer) & Q(company=company)
            ChatHistory.objects.filter(qry_filter).update(saved_status=True)

            # Create new Chat history
            talker = User.objects.filter(Q(company=company.parent_company) & Q(role='admin'))
            talker = talker[0]
            chat_hist = ChatHistory.objects.create(
                company=company,
                chat_type='bot_chat',
                customer=customer,
                talker=talker
            )

            sentence_list = [company.bot_name, company.intro_ques, company.bot_title, 'Book Appointment',
                             company.bot_ques]
            variable_list = ['bot_name', 'intro_ques', 'bot_title', 'appointment_title', 'bot_ques']
            if language == company.language:
                data = dict(zip(variable_list, sentence_list))
            else:
                translate = Translator()
                translated_lines = translate.translate(sentence_list, src=company.language, dest=language)
                data = dict(zip(variable_list, [i.text for i in translated_lines]))

            chat_titles = {}
            for i in company.company_chat_title.all():
                if i.active:
                    if language == company.language:
                        chat_titles[i.pk] = i.title
                    else:
                        chat_titles[i.pk] = translate.translate(i.title, src=company.language, dest=language).text

            data['customer_key'] = u_id
            data['language'] = language
            data['chat_titles'] = chat_titles
            response = {'status': True, 'message': 'success', 'data': data}

        else:
            response = serializer_error(serializer.errors.items())

        return Response(response)


class BotReplyView(APIView):
    permission_classes = (Check_API_KEY_Auth,)

    def post(self, request, *args, **kwargs):
        company = CompanyModel.objects.filter(secret_key=kwargs['secret_key'])
        if not company:
            response = {'status': False, 'message': 'Incorrect secret key in url.'}
            return Response(response)
        else:
            company = company[0]

        company_name = company.name[:10] if len(company.name) > 10 else company.name
        dir_name = 'company_files/' + str(company.id) + '_' + company_name + '/'
        company_lang = company.language

        serializer = BotReplySerializer(data=request.data)
        if serializer.is_valid():
            question = serializer['question'].value
            user_lang = serializer['language'].value
            customer_key = serializer['customer_key'].value

            if company_lang != user_lang:
                translate = Translator()
                question = translate.translate(question, src=user_lang, dest=company_lang).text

            if_trained = Question.objects.filter(Q(question_tag__company=company) & Q(if_trained=True)).exists()
            try:
                if if_trained:
                    reply = bot_reply(question, dir_name)
                else:
                    reply = 'System can not answer this question. Would you like to talk to our customer care service.'
            except:
                reply = 'System can not answer this question. Would you like to talk to our customer care service.'

            customer = Customer.objects.get(u_field=customer_key)
            qry_filter = Q(saved_status=False) & Q(customer=customer) & Q(company=company)
            Conversation.objects.create(
                history=ChatHistory.objects.filter(qry_filter)[0],
                question=question,
                answer=reply,
            )

            if company_lang != user_lang:
                translate = Translator()
                reply = translate.translate(reply, src=company_lang, dest=user_lang).text

            response = {'status': True, 'message': 'success', 'data': reply}

        else:
            response = serializer_error(serializer.errors.items())

        return Response(response)


class StartChatView(APIView):
    permission_classes = (Check_API_KEY_Auth,)

    def post(self, request):
        serializer = StartChatSerializer(data=request.data)
        if serializer.is_valid():
            main_type = serializer['main_type'].value
            user_lang = serializer['user_lang'].value
            title_pk = serializer['title_pk'].value
            option_number = serializer['option_number'].value
            number = serializer['number'].value

            data_1 = get_title_pk(main_type, title_pk, option_number, number)

            if not data_1['status']:
                response = {'status': False, 'message': data_1['message']}
                return Response(response)

            title_pk = data_1['title_pk']

            data = start_chat_view(title_pk, user_lang)

            if not data['status']:
                response = {"status": False, "message": "Something went wrong"}
            else:
                if data['carousel_type'] == 'single':
                    if data['detail']['image']:
                        data['detail']['image'] = request.build_absolute_uri(data['detail']['image'])
                elif data['carousel_type'] == 'carousel':
                    for i in data['detail']:
                        if i['image']:
                            i['image'] = request.build_absolute_uri(i['images'])

                response = {'status': True, 'message': 'success', 'data': data}

        else:
            response = serializer_error(serializer.errors.items())

        return Response(response)


class ServiceProviderView(APIView):
    permission_classes = (Check_API_KEY_Auth,)

    def post(self, request):
        serializer = ServiceProviderSerializer(data=request.data)
        if serializer.is_valid():
            secret_key = serializer['secret_key'].value
            user_lang = serializer['language'].value
            pk = get_object_or_404(Company, secret_key=secret_key).pk
            data = service_provider_view(pk, user_lang)
            if data['status']:
                response = {'status': True, 'message': 'success', 'data': data}
            else:
                response = {'status': False, 'message': data['message']}
        else:
            response = serializer_error(serializer.errors.items())

        return Response(response)


class GetSlotView(APIView):
    permission_classes = (Check_API_KEY_Auth,)

    def post(self, request):
        serializer = GetSlotSerializer(data=request.data)
        if serializer.is_valid():
            pk = serializer['pk'].value
            user_lang = serializer['language'].value
            date = serializer['date'].value

            data = get_slots(pk, date, user_lang)
            if data['status']:
                response = {'status': True, 'message': 'success', 'data': data}
            else:
                response = {'status': False, 'message': data['message']}

        else:
            response = serializer_error(serializer.errors.items())

        return Response(response)


class BookSelectedSlotView(APIView):
    permission_classes = (Check_API_KEY_Auth,)

    def post(self, request):
        serializer = BookSelectedSlotSerializer(data=request.data)
        if serializer.is_valid():
            slot_pk = serializer['slot_pk'].value
            date = serializer['date'].value
            slot_time = serializer['slot_time'].value
            provider_pk = serializer['provider_pk'].value
            u_id = serializer['u_id'].value

            data = book_selected_slot_view(slot_pk, date, slot_time, provider_pk, u_id)

            if data['status']:
                response = {'status': True, 'message': 'Confirmation mail has been sent to email ID provided by you.'}

            else:
                response = {'status': False, 'message': 'Something went wrong'}

        else:
            response = serializer_error(serializer.errors.items())

        return Response(response)


class LanguageList(APIView):
    permission_classes = (Check_API_KEY_Auth, )

    def get(self, request):
        response = {'status': True, 'message': 'Success', 'data': {'language': [googletrans.LANGUAGES]}}
        return Response(response)


class GetColors(APIView):
    permission_classes = (Check_API_KEY_Auth,)

    def post(self, request):
        serializer = GetColorSerializer(data=request.data)
        if serializer.is_valid():
            secret_key = serializer['secret_key'].value
            company = Company.objects.filter(secret_key=secret_key)
            if company:
                company = company[0]
                if company.image:
                    image = request.build_absolute_uri(company.image.url)
                else:
                    image = ""
                text = 'Hi! I am '+company.bot_name
                # translate = Translator()
                # intro_text = translate.translate(text, src='en', dest=company.language).text
                data = {'color': company.color, 'text_color': company.head_text_color,
                        'instruction_text': company.intro_text_login, 'image': image, 'bot_name': company.bot_name,
                        'is_active': company.active, 'intro_text': text}

                response = {'status': True, 'message': 'Success', 'data': data}
            else:
                response = {'status': False, 'message': 'Invalid Secret Key'}
        else:
            response = serializer_error(serializer.errors.items())

        return Response(response)


class StartBotChat(APIView):
    permission_classes = (Check_API_KEY_Auth,)

    def post(self, request):
        serializer = ServiceProviderSerializer(data=request.data)
        if serializer.is_valid():
            secret_key = serializer['secret_key'].value
            language = serializer['language'].value
            company = Company.objects.filter(secret_key=secret_key)

            if company:
                company = company[0]
                translate = Translator()
                if company.language == language:
                    line = company.bot_ques
                else:
                    line = translate.translate(company.bot_ques, src=company.language, dest=language).text
                data = {'line': line}
                response = {'status': True, 'message': 'Success', 'data': data}

            else:
                response = {'status': False, 'message': 'Invalid Secret Key'}

        else:
            response = serializer_error(serializer.errors.items())

        return Response(response)


class ChangeLanguage(APIView):
    permission_classes = (Check_API_KEY_Auth,)

    def post(self, request):
        serializer = ChangeLanguageSerializer(data=request.data)

        if serializer.is_valid():
            intro_text = serializer['intro_text'].value
            instruction_text = serializer['instruction_text'].value
            curr_lang = serializer['curr_lang'].value
            dest_lang = serializer['dest_lang'].value
            translator = Translator()
            try:
                intro_text = translator.translate(intro_text, src=curr_lang, dest=dest_lang).text
                instruction_text = translator.translate(instruction_text, src=curr_lang, dest=dest_lang).text
                start_chat = translator.translate("Start Chat", src=curr_lang, dest=dest_lang).text
                data = {'intro_text': intro_text, 'instruction_text': instruction_text, 'start_chat': start_chat}
                response = {'status': True, 'message': 'Success', 'data': data}
            except:
                try:
                    intro_text = translator.translate(intro_text, src=curr_lang, dest=dest_lang).text
                    instruction_text = translator.translate(instruction_text, src=curr_lang, dest=dest_lang).text
                    start_chat = translator.translate("Start Chat", src=curr_lang, dest=dest_lang).text
                    data = {'intro_text': intro_text, 'instruction_text': instruction_text, 'start_chat': start_chat}
                    response = {'status': True, 'message': 'Success', 'data': data}
                except:
                    response = {
                        'status': False,
                        'message': "Something went wrong. Please try after 5 sec",
                    }


        else:
            response = serializer_error(serializer.errors.items())

        return Response(response)


class AfterSlotClick(APIView):
    permission_classes = (Check_API_KEY_Auth,)

    def post(self, request):
        serializer = IntroLanguageChangeSerializer(data=request.data)

        if serializer.is_valid():
            lang = serializer['language'].value
            detail_line = "Your booking details:"
            name_line = "Name"
            slot_line = "Slot"
            date_line = "Date"
            instruction = "Click 'Yes' to book this slot"
            if lang != 'en':
                translate = Translator()
                detail_line = translate.translate(detail_line, src='en', dest=lang).text
                name_line = translate.translate(name_line, src='en', dest=lang).text
                slot_line = translate.translate(slot_line, src='en', dest=lang).text
                date_line = translate.translate(date_line, src='en', dest=lang).text
                instruction = translate.translate(instruction, src='en', dest=lang).text

            data = {'detail_line': detail_line, 'name_line': name_line, 'slot_line': slot_line,
                        'date_line': date_line, 'instruction': instruction}
            response = {'status': True, 'message': 'Success', 'data': data}
        else:
            response = serializer_error(serializer.errors.items())

        return Response(response)
