from django.forms import ModelForm
from django import forms
from .models import *


class ChatmessageCreateForm(ModelForm):
    body = forms.CharField(label='', widget=forms.TextInput(attrs={
        'placeholder': 'Add message ...',
        'class': 'p-4 text-black',
        'maxlength': '300',
        'autofocus': True,
        'style': 'width: 1000px;'
    }))

    class Meta:
        model = GroupMessage
        fields = ['body']

class NewGroupForm(forms.ModelForm):
    class Meta:
        model = ChatGroup
        fields = ['groupchat_name', 'group_image']
        widgets = {
            'groupchat_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md mt-2 mb-2',
                'max_length': '300',
                'placeholder': 'Enter group chat name',
            }),
            'group_image': forms.ClearableFileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md mt-2 mb-2',
                'accept': 'image/*'
            }),
        }

class ChatRoomEditForm(forms.ModelForm):
    group_image = forms.ImageField(
        label='Group Image',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md mt-6',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = ChatGroup
        fields = ['groupchat_name', 'group_image']
        widgets = {
            'groupchat_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'max_length': '300',
                'placeholder': 'Enter group chat name',
            }),
        }