from django import forms
from .models import Notification, SingleMatch, Tournament
from academy.models import Band
from django.contrib.contenttypes.models import ContentType
from academy.models import Player, Championship

class SingleMatchForm(forms.ModelForm):
    class Meta:
        model = SingleMatch
        fields = ['name', 'date', 'tournament', 'player_1', 'player_2', 'price_amount', 'entry_amount', 'is_championship_match']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control'
            }),
            'tournament': forms.Select(attrs={'class': 'form-select'})
        }

    tournament = forms.ModelChoiceField(
        queryset=Tournament.objects.filter(is_completed=False).order_by("date", "-updated_at"),
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

class PlayerSelectionFilterForm(forms.Form):
    bands = forms.ModelMultipleChoiceField(
        queryset=Band.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={"onchange": "this.form.submit();"})
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
    include_champion = forms.BooleanField(
        label="Include Champions",
        required=False,
        widget=forms.CheckboxInput(attrs={"onchange": "this.form.submit();"})
    )
    sort_by = forms.ChoiceField(
        choices=[
            ("", "Default (Win % High → Low)"),
            ("name", "Name (A-Z)"),
            ("-name", "Name (Z-A)"),
            ("wins", "Wins (Low → High)"),
            ("-wins", "Wins (High → Low)"),
            ("winningpercentage", "Win % (Low → High)"),
            ("-winningpercentage", "Win % (High → Low)"),
            ("networth", "Networth (Low → High)"),
            ("-networth", "Networth (High → Low)"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-select", "onchange": "this.form.submit();"})
    )

    def filter_queryset(self, queryset):
        bands = self.cleaned_data.get("bands")
        gender = self.cleaned_data.get("gender")
        is_champion = self.cleaned_data.get("is_champion")
        include_champion = self.cleaned_data.get("include_champion")
        sort_by = self.cleaned_data.get("sort_by")

        if bands and bands.exists():
            queryset = queryset.filter(band__in=bands)
        if gender:
            queryset = queryset.filter(gender=gender)
        if is_champion:
            champion_ids = Championship.objects.values_list("player_id", flat=True)
            queryset = queryset.filter(id__in=champion_ids)
        if not include_champion:
            champion_ids = Championship.objects.values_list("player_id", flat=True)
            queryset = queryset.exclude(id__in=champion_ids)

        if sort_by:
            queryset = queryset.order_by(sort_by)
        else:
            queryset = queryset.order_by("-winningpercentage")
        return queryset
    
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

    price_amount = forms.FloatField(
        label="Prize Amount",
        required=False,
        min_value=0,
        initial=0
    )

    entry_amount = forms.FloatField(
        label="Entry Amount",
        required=False,
        min_value=0,
        initial=0
    )

    is_championship_match = forms.BooleanField(
        label="Is this a Championship Match?",
        required=False,
        initial=False,
        help_text="Tick this if the match determines a championship winner."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customize label for each player
        champions = set(
            Championship.objects.values_list("player_id", flat=True)
        )

        self.fields["players"].label_from_instance = lambda player: (
            f"""{player.band.emoji or ''} {player.name}{' ©️' if player.id in champions else ''} | {'M' if player.gender == "Male" else 'F'} | {round(player.winningpercentage, 2)}%"""
        ).strip()

class ChampionshipChoiceField(forms.ModelChoiceField):
    """Custom field to display championship name + holder."""
    def label_from_instance(self, obj):
        holder_name = obj.player.name if obj.player else "No current holder"
        return f"{obj.name} — {holder_name}"

class ChampionshipChallengeForm(forms.ModelForm):
    championship = ChampionshipChoiceField(
        queryset=Championship.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    tournament = forms.ModelChoiceField(
        queryset=Tournament.objects.filter(is_completed=False).order_by("date", "-updated_at"),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = SingleMatch
        fields = ['name', 'date', 'championship', 'tournament', 'price_amount', 'entry_amount']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'price_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'entry_amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }