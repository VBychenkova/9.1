from django import forms
from .models import Post
from django.utils.translation import gettext_lazy as _

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'categories']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'categories': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

class ContactForm(forms.Form):
    name = forms.CharField(label=_('Your Name'))
    email = forms.EmailField(label=_('Email Address'))
    message = forms.CharField(label=_('Message'), widget=forms.Textarea)