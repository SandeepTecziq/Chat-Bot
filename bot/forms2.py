from django import forms
from .models import SubscriptionPlan


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


