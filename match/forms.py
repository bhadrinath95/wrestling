from django import forms
from .models import Notification, SingleMatch
from django.contrib.contenttypes.models import ContentType
from academy.models import Player

class SingleMatchForm(forms.ModelForm):
    class Meta:
        model = SingleMatch
        fields = ['name', 'player_1', 'player_2', 'date', 'price_amount', 'entry_amount']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',  # HTML5 date picker
                'class': 'form-control'
            }),
        }

    player_1 = forms.ModelChoiceField(
        queryset=Player.objects.all().order_by("name"),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Player 1"
    )

    player_2 = forms.ModelChoiceField(
        queryset=Player.objects.all().order_by("name"),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Player 2"
    )

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter notification...'
            }),
        }