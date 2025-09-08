from django import forms
from .models import Band, Player, Championship

class BandForm(forms.ModelForm):
    class Meta:
        model = Band
        fields = '__all__'

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = '__all__'

class ChampionshipForm(forms.ModelForm):
    class Meta:
        model = Championship
        fields = '__all__'

class PlayerFilterForm(forms.Form):
    band = forms.ModelChoiceField(
        queryset=Band.objects.all(),
        required=False,
        empty_label="All Bands",
        widget=forms.Select(attrs={"class": "form-select", "onchange": "this.form.submit();"})
    )

    gender = forms.ChoiceField(
        choices=[("", "All Genders")] + list(Player.GENDER_CHOICES),
        required=False,
        widget=forms.Select(attrs={"class": "form-select", "onchange": "this.form.submit();"})
    )