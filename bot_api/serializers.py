from rest_framework import serializers


class IntroLanguageChangeSerializer(serializers.Serializer):
    language = serializers.CharField(max_length=3)


class GetUserDetailSerializer(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.EmailField()
    language = serializers.CharField()


class BotReplySerializer(serializers.Serializer):
    question = serializers.CharField()
    language = serializers.CharField()
    customer_key = serializers.CharField()


class StartChatSerializer(serializers.Serializer):
    main_type = serializers.CharField()
    user_lang = serializers.CharField()
    title_pk = serializers.CharField()
    option_number = serializers.CharField()
    number = serializers.CharField()


class NextQuestionSerializer(serializers.Serializer):
    language = serializers.CharField()
    pk = serializers.CharField()
    number = serializers.CharField()


class ServiceProviderSerializer(serializers.Serializer):
    language = serializers.CharField()
    secret_key = serializers.CharField()


class GetSlotSerializer(serializers.Serializer):
    pk = serializers.CharField()
    date = serializers.CharField()
    language = serializers.CharField()


class BookSelectedSlotSerializer(serializers.Serializer):
    slot_pk = serializers.CharField()
    date = serializers.CharField()
    slot_time = serializers.CharField()
    provider_pk = serializers.CharField()
    u_id = serializers.CharField()


class GetColorSerializer(serializers.Serializer):
    secret_key = serializers.CharField()


class ChangeLanguageSerializer(serializers.Serializer):
    intro_text = serializers.CharField()
    instruction_text = serializers.CharField()
    curr_lang = serializers.CharField()
    dest_lang = serializers.CharField()