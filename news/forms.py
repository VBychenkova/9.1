from django import forms
from .models import Post, Article, News, Category
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

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'category', 'is_published']
        labels = {
            'title': _('Title'),
            'content': _('Content'),
            'category': _('Category'),
            'is_published': _('Publish immediately'),
        }
        help_texts = {
            'title': _('Enter the title of your article'),
            'content': _('Write the content of your article'),
        }

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content', 'categories', 'is_published']
        labels = {
            'title': _('Title'),
            'content': _('Content'),
            'categories': _('Categories'),
            'is_published': _('Publish immediately'),
        }

#class CategoryForm(forms.ModelForm):
#    class Meta:
#        model = Category
#        fields = ['name']
#        labels = {
#            'name': _('Category Name'),
#        }