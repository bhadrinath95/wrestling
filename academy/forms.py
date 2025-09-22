from django import forms
from .models import Band, Player, Championship, Rule

class BandForm(forms.ModelForm):
    class Meta:
        model = Band
        fields = '__all__'

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['name', 'gender', 'band', 'wins', 'matchesplayed', 'networth', 'image_url', 'spouse']

class ChampionshipForm(forms.ModelForm):
    class Meta:
        model = Championship
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['player'].queryset = Player.objects.all().order_by('name')

class RuleForm(forms.ModelForm):
    class Meta:
        model = Rule
        fields = '__all__'

class PlayerFilterForm(forms.Form):
    bands = forms.ModelMultipleChoiceField(
        queryset=Band.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={"onchange": "this.form.submit();"}
        )
    )
    gender = forms.ChoiceField(
        choices=[("", "All Genders")] + list(Player.GENDER_CHOICES),
        required=False,
        widget=forms.Select(attrs={"class": "form-select", "onchange": "this.form.submit();"})
    )
    is_champion = forms.BooleanField(
        label="Only Champions",
        required=False,
        widget=forms.CheckboxInput(attrs={"onchange": "this.form.submit();"})
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
