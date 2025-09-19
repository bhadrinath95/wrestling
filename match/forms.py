from django import forms
from .models import Notification, SingleMatch, Tournament
from academy.models import Band
from django.contrib.contenttypes.models import ContentType
from academy.models import Player, Championship

class SingleMatchForm(forms.ModelForm):
    class Meta:
        model = SingleMatch
        fields = ['name', 'date', 'tournament', 'player_1', 'player_2', 'price_amount', 'entry_amount']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control'
            }),
            'tournament': forms.Select(attrs={'class': 'form-select'})
        }

    tournament = forms.ModelChoiceField(
        queryset=Tournament.objects.all().order_by("-updated_at"),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

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


class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            )
        }

class CreateLeagueForm(forms.ModelForm):
    gender = forms.ChoiceField(
        choices=[("Male", "Male"), ("Female", "Female"), ("Both", "Both")],
        required=False
    )
    bands = forms.ModelMultipleChoiceField(
        queryset=Band.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    price_amount = forms.FloatField(required=False)
    entry_amount = forms.FloatField(required=False)

    class Meta:
        model = Tournament   # or SingleMatch depending on what you intend
        fields = []

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

class CreateMatchSetupForm(forms.Form):
    match_name = forms.CharField(
        label="Match Name Prefix",
        max_length=100,
        required=False,
        help_text="Optional. Example: 'League', matches will be named 'League Match 1', 'League Match 2', etc."
    )

    players = forms.ModelMultipleChoiceField(
        queryset=Player.objects.all().order_by("-winningpercentage"),
        widget=forms.CheckboxSelectMultiple,
        label="Select Players"
    )

    price_amount = forms.DecimalField(
        label="Prize Amount",
        required=False,
        min_value=0,
        decimal_places=2,
        max_digits=10,
        initial=0
    )

    entry_amount = forms.DecimalField(
        label="Entry Amount",
        required=False,
        min_value=0,
        decimal_places=2,
        max_digits=10,
        initial=0
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customize label for each player
        champions = set(
            Championship.objects.values_list("player_id", flat=True)
        )

        self.fields["players"].label_from_instance = lambda player: (
            f"{player.band.emoji or ''} {player.name}{' ©️' if player.id in champions else ''} | {'M' if player.gender == "Male" else 'F'} | {round(player.winningpercentage, 2)}%"
        ).strip()