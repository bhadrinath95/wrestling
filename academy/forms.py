from django import forms
from .models import Band, Player, Championship, Rule

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

class RuleForm(forms.ModelForm):
    class Meta:
        model = Rule
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

    sort_by = forms.ChoiceField(
        choices=[
            ("", "Default (Name)"),
            ("name", "Name (A-Z)"),
            ("-name", "Name (Z-A)"),
            ("wins", "Wins (Low → High)"),
            ("-wins", "Wins (High → Low)"),
             ("winningpercentage", "Win % (Low → High)"),
            ("-winningpercentage", "Win % (High → Low)"),
            ("matchesplayed", "Matches (Low → High)"),
            ("-matchesplayed", "Matches (High → Low)"),
            ("networth", "Networth (Low → High)"),
            ("-networth", "Networth (High → Low)"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-select", "onchange": "this.form.submit();"})
    )