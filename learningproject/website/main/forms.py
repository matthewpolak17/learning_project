from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, Question, Subject, Reply, User, Answer

#registers a new user
class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "password1", "password2", "is_teacher", "is_student"]

#logs the user in
class LoginForm(forms.Form):
    username = forms.CharField(
        widget= forms.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )

#post creation form
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "description"]

#post full form goes with post form and allows the user to add multiple files to their post
class PostFullForm(PostForm):
    files = forms.FileField(widget=forms.ClearableFileInput(attrs={'allow_multiple_selected': True}), required=False)
    class Meta(PostForm.Meta):
        fields = PostForm.Meta.fields + ['files',]

#reply form
class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ["description",]

#subject creation form
class SubjectSetupForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ["title",]

#question creation form
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["text",]

#answer creation form
class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ["text", "is_correct"]

        





