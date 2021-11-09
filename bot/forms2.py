from django import forms
from .models import SubscriptionPlan, ChatTitle, SurveyQuestion, SurveyOptions, ProviderCategory
from django.db.models import Q


class QuestionForm(forms.ModelForm):
    class Meta:
        model = SurveyQuestion
        fields = ('type', 'ans_type', 'question', 'prt_question', 'prt_option', 'image', 'url',
                  'question_form_type')
        widgets = {
            'type': forms.TextInput(attrs={'hidden': True}),
            'ans_type': forms.TextInput(attrs={'hidden': True}),
            'question_form_type': forms.TextInput(attrs={'hidden': True}),
            'question': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'prt_question': forms.Select(attrs={'class': 'form-control question-select'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        title_id = kwargs.pop('title_pk')
        super().__init__(*args, **kwargs)
        self.fields['prt_question'].queryset = SurveyQuestion.objects.filter(chat_title__pk=title_id)


class OptionForm(forms.ModelForm):
    class Meta:
        model = SurveyOptions
        fields = ('image', 'option', 'text', 'url')
        widgets = {
            'option': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.question_form_type = kwargs.pop('question_form_type')
        super().__init__(*args, **kwargs)

    def clean_option(self):
        option = self.cleaned_data.get('option')
        if self.question_form_type in ['text-option', 'carousel-option']:
            if not option:
                raise forms.ValidationError("All option fields are required for this question type.")
        return option

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if self.question_form_type in ['image-carousel', 'carousel-option']:
            if not image:
                raise forms.ValidationError("All image fields are required for this question type.")
        return image


class CreateSubscriptionForm(forms.ModelForm):
    class Meta:
        model = SubscriptionPlan
        fields = ('name', 'price', 'currency', 'bot_allowed', 'is_default')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Plan Name *'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price *'}),
            'currency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Currency *'}),
            'bot_allowed': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'No. of Bot Allowed *'}),
        }


class ChatTitleForm(forms.ModelForm):
    class Meta:
        model = ChatTitle
        fields = ('title',)
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control decorated-input w-75 d-inline',
                                            'placeholder': 'Enter title of chat map'})
        }


class ProviderCategoryForm(forms.ModelForm):
    class Meta:
        model = ProviderCategory
        fields = ('name', 'company')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'provider-name', 'placeholder': 'Enter name of category'})
        }

