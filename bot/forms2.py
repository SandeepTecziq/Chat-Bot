from django import forms
from .models import SubscriptionPlan, ChatTitle, SurveyQuestion, SurveyOptions
from django.db.models import Q


class QuestionForm(forms.ModelForm):
    class Meta:
        model = SurveyQuestion
        fields = ('type', 'ans_type', 'question', 'prt_question', 'prt_option', 'image', 'url')
        widgets = {
            'type': forms.TextInput(attrs={'hidden': True}),
            'ans_type': forms.TextInput(attrs={'hidden': True}),
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


class ChatNewForm(forms.Form):
    number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-number', 'disabled': 'disabled'}))
    u_id = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-u-id'}))
    child_id = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-child-id'}))
    carousel_type = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-carousel-type'}))
    parent = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-parent'}), required=False)
    chat_title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-chat-title'}))
    question = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-text-single',
                                                             'placeholder': 'Enter Your Question'}))
    is_option = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-is-option'}))
    form_type = forms.CharField(widget=forms.TextInput(attrs={'hidden': 'hidden', 'class': 'form_type'}))

    def clean_question(self):
        question = self.cleaned_data['question']
        if not question:
            return forms.ValidationError('Question field is required')

        return question


class SingleChatForm(forms.Form):
    image = forms.ImageField(required=False)
    url = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'url-input',
                                                                      'placeholder': 'Add URL (Optional)'
                                                                      }))
    single_text = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'single-text',
                                                                'placeholder': 'Card Title (Optional)'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-description',
                                                                               'placeholder': 'Card Body'}))


class CarouselChatForm(forms.Form):
    image = forms.ImageField(required=False)
    child_id = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-option-child-id',
                                                                             'hidden': 'hidden'}))
    option = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-option',
                                                                           'placeholder': 'Option',}))
    text = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-text-carousel',
                                                                         'placeholder': 'Title',}))
    number_option = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-number',
                                                                           'placeholder': 'Add URL (Optional)',
                                                                           'disabled': 'disabled'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-description',
                                                                               'placeholder': 'Card Body'}))


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
