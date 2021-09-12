from django import forms
from django.forms import BaseFormSet
from .models import Customer, User, Company, ServiceProvider, TimeSlots, BookedSlots, FacebookBotDetails, ParentCompany
from django.contrib.auth import authenticate
from django.contrib.admin import widgets


class RequiredFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(RequiredFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False


class AddQuestionForm(forms.Form):
    tag = forms.CharField(max_length=30, required=False, widget=forms.TextInput({'hidden': 'hidden'}))
    question = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter Question', 'class': 'form-text-area'}))
    answer = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter Answer', 'class': 'form-text-area'}))

    def clean_question(self):
        question = self.cleaned_data.get('question')

        if question == "":
            raise forms.ValidationError('This field is required.')

        return question

    def clean_answer(self):
        answer = self.cleaned_data.get('answer')

        if answer == "":
            raise forms.ValidationError('This field is required.')

        return answer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('name', 'email')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control popup-form-input',
                                           'placeholder': 'name *'}),
            'email': forms.EmailInput(attrs={'class': 'form-control popup-form-input',
                                             'placeholder': 'email *'}),
        }


class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=30,
                               widget=forms.TextInput(attrs={'class': 'login-input', 'id': 'inputEmail'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'login-input'}))

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if username == "":
            raise forms.ValidationError('This field is required.')

        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')

        if password == "":
            raise forms.ValidationError('This field is required.')

        return password

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError('Username or Password is incorrect')
        return self.cleaned_data

    def login(self, request):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user.is_active:
            return forms.ValidationError('User is not active.')
        return user


class ParentCompanyForm(forms.ModelForm):
    class Meta:
        model = ParentCompany
        fields = ('name', )
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name *'}),
        }


class CreateUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                 'placeholder': 'Password *'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                 'placeholder': 'Confirm Password *'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password', 'confirm_password', 'bots')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username *'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email *'}),
            'bots': forms.SelectMultiple(attrs={'class': 'select-bot selectpicker', 'placeholder': 'Select Bot'})
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if not email:
            raise forms.ValidationError(
                "This field is required."
            )
        user = User.objects.filter(email=email).exists()
        if user:
            raise forms.ValidationError(
                "This email has been register."
            )

        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')

        user = User.objects.filter(username=username).exists()
        if user:
            raise forms.ValidationError(
                "This username has been register."
            )

        return username

    def clean(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "Password and Confirm Password does not match"
            )


class AddBotToUser(forms.ModelForm):
    class Meta:
        model = User
        fields = ('bots', )
        widgets = {
            'bots': forms.SelectMultiple(attrs={'class': 'select-bot selectpicker', 'placeholder': 'Select Bot'})
        }


class UpdateBotForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ('bot_name', 'image', 'color', 'intro_ques', 'bot_title', 'bot_ques', 'head_text_color',
                  'service_provider', 'intro_text_login')
        widgets = {
            'bot_name': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'intro_ques': forms.TextInput(attrs={'class': 'form-control'}),
            'bot_title': forms.TextInput(attrs={'class': 'form-control'}),
            'bot_ques': forms.TextInput(attrs={'class': 'form-control'}),
            'head_text_color': forms.TextInput(attrs={'class': 'form-control'}),
            'intro_text_login': forms.TextInput(attrs={'class': 'form-control'}),
            'service_provider': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CreateCompany(forms.ModelForm):
    class Meta:
        model = Company
        fields = ('name', 'language', 'bot_name', 'service_provider', 'image', 'color', 'intro_ques', 'bot_ques', 'bot_title',
                  'head_text_color', 'intro_text_login', 'provider_line', 'slot_line',
                  'ques_color', 'backup_line', 'bot_introduction')
        widgets = {
            'language': forms.Select(attrs={'class': 'selectpicker choose-language', 'data-live-search': 'true'})
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if not all(x.isalpha() or x.isspace() for x in name):
            return forms.ValidationError("Only letters and space is allowed.")

        return name


class CreateAdmin(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password')


class CreateProviderForm(forms.ModelForm):
    class Meta:
        model = ServiceProvider
        fields = ('name', )
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter name of Provider', 'class': 'provider-name'})
        }


class TimeSlotForm(forms.ModelForm):
    DAYS = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
        ('All', 'All')
    )
    start = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'HH:MM'}))
    end = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'HH:MM'}))
    provider = forms.CharField(widget=forms.TextInput(attrs={'hidden': 'hidden'}))

    class Meta:
        model = TimeSlots
        fields = ('start', 'end', 'provider')


class ChangePasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                 'placeholder': 'Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                         'placeholder': 'Confirm Password'}))

    def clean(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "password and confirm_password does not match"
            )


class ForgetPasswordForm(forms.Form):
    username = forms.CharField()

    def clean_username(self):
        username = self.cleaned_data['username']
        user_exist = User.objects.filter(username=username).exists()
        if username == "":
            raise forms.ValidationError('This field is required.')

        if not user_exist:
            raise forms.ValidationError('This username has not been registered. Please contact to admin.')

        user = User.objects.get(username=username)
        email = user.email

        if not email:
            raise forms.ValidationError('Email ID for account with this username has not been provided. Please contact to admin.')

        return username


class FacebookBotDetailForm(forms.ModelForm):
    class Meta:
        model = FacebookBotDetails
        fields = ('access_key', 'page_id')
        widgets = {
            'access_key': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Access Token'}),
            'page_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Page ID'})
        }
