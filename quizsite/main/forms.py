from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import *


class CreateTestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['name', 'description', 'question_quantity']


class CreateQuestionsForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question', 'correct_answer', 'incorrect_answer_1', 'incorrect_answer_2', 'incorrect_answer_3']


class QuestionForm(forms.Form):
    answer = forms.ChoiceField(widget=forms.RadioSelect())

    def __init__(self, *args, **kwargs):
        question_name = kwargs.pop('question_name')
        choices = kwargs.pop('choices')
        question_number = kwargs.pop('question_number')
        question_quantity = kwargs.pop('question_quantity')
        super().__init__(*args, **kwargs)
        self.question_number = question_number
        self.question_quantity = question_quantity
        self.fields['answer'].choices = choices
        self.fields['answer'].label = question_name


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
