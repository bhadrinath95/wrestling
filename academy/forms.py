from django import forms
from .models import Band, Player

class BandForm(forms.ModelForm):
    class Meta:
        model = Band
        fields = '__all__'

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = '__all__'