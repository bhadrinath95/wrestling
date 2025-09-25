from django.shortcuts import render, get_object_or_404, redirect
from .models import Band, Player, Championship, Rule, Auction, ChampionshipHistory
from .forms import BandForm, PlayerForm, ChampionshipForm, PlayerFilterForm, RuleForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
import random
from django.utils import timezone
from match.models import Tournament


def home_view(request):
    return render(request, 'home.html', {})

def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

@login_required
def band_list(request):
    bands = Band.objects.all().order_by('name')
    return render(request, 'academy/bands/band_list.html', {'bands': bands})

@login_required
def band_create(request):
    form_name = "Create Band"
    if request.method == "POST":
        form = BandForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('band-list')
    else:
        form = BandForm()
    return render(request, 'form.html', {'form': form, "form_name": form_name, 'list_url': reverse('band-list'), })

@login_required
def band_update(request, pk):
    form_name = "Update Band"
    band = get_object_or_404(Band, pk=pk)
    if request.method == "POST":
        form = BandForm(request.POST, instance=band)
        if form.is_valid():
            form.save()
            return redirect('band-list')
    else:
        form = BandForm(instance=band)
    return render(request, 'form.html', {'form': form, "form_name": form_name, 'list_url': reverse('band-list'), })

@login_required
def band_delete(request, pk):
    instance = get_object_or_404(Band, pk=pk)
    if request.method == "POST":
        instance.delete()
        if request.htmx:
            bands = Band.objects.all()
            return render(request, "academy/bands/partials/table_body.html", {"bands": bands})

    return render(
        request,
        "partials/confirm_delete.html",
        {"instance": instance, "reverse_url": reverse("band-list"), "delete_view_name": "band-delete"},
    )

def get_player_object_list(form):
    players = Player.objects.all().order_by("name")
    if form.is_valid():
        bands = form.cleaned_data.get("bands")
        gender = form.cleaned_data.get("gender")
        sort_by = form.cleaned_data.get("sort_by")
        is_champion = form.cleaned_data.get("is_champion")

        if is_champion:
            players = players.filter(championship__isnull=False)
        if bands:
            players = players.filter(band__in=bands)
        if gender:
            players = players.filter(gender=gender)
        if sort_by:
            players = players.order_by(sort_by)
        else:
            players = players.order_by("name")
    return players

@login_required
def player_list(request):
    form = PlayerFilterForm(request.GET or None)
    players = get_player_object_list(form)
    return render(
        request,
        "academy/players/player_list.html",
        {"players": players, "form": form, 'title': 'Players List',},
    )

@login_required
def player_images(request):
    form = PlayerFilterForm(request.GET or None)
    players = get_player_object_list(form)
    return render(
        request,
        "academy/players/player_image.html",
        {"players": players, "form": form, 'title': 'Players Show',},
    )

@login_required
def player_create(request):
    form_name = "Create Player"
    if request.method == "POST":
        form = PlayerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('player-list')
    else:
        form = PlayerForm()
    return render(request, 'form.html', {'form': form, "form_name": form_name, 'list_url': reverse('player-list'), })

@login_required
def permanently_delete(request, pk):
    instance = get_object_or_404(Player.all_objects, pk=pk)
    instance.delete()
    return redirect('player-list')

@login_required
def player_update(request, pk):
    form_name = "Update Player"
    player = get_object_or_404(Player.all_objects, pk=pk)
    if request.method == "POST":
        form = PlayerForm(request.POST, instance=player)
        if form.is_valid():
            form.save()
            return redirect('player-list')
    else:
        form = PlayerForm(instance=player)
    return render(request, 'form.html', {'form': form, "form_name": form_name, 'list_url': reverse('player-list'), })

@login_required
def player_auction(request, pk):
    player = get_object_or_404(Player, pk=pk)

    if player.band is None or player.band.name != "NXT Generations Band":
        message = "This player is not eligible for auction (not in NXT Generations Band)."
        return render(request, 'academy/players/player_view.html', {'instance': player, 'message': message})

    min_networth = (2 / 3) * player.networth
    eligible_bands = Band.objects.exclude(name="NXT Generations Band").filter(networth__gte=min_networth)

    if not eligible_bands.exists():
        message = "No eligible band found for this auction."
        return render(request, 'academy/players/player_view.html', {'instance': player, "message": message})

    selected_band = random.choice(list(eligible_bands))
    old_band = player.band

    with transaction.atomic():
        player.band = selected_band
        player.save()

        selected_band.networth -= player.networth
        selected_band.save()

        Auction.objects.create(
            player=player,
            from_band=old_band,
            to_band=selected_band,
            price=player.networth,
        )

    message = f"{player.name} auctioned from {old_band.name} to {selected_band.name}!. Remaining Band Networth: {selected_band.networth:.2f}."

    return render(request, 'academy/players/player_view.html', {'instance': player, "message": message})


@login_required
def player_delete(request, pk):
    instance = get_object_or_404(Player, pk=pk)
    if request.method == "POST":
        instance.networth = 0
        instance.is_active = False
        instance.save()
        
        if request.htmx:
            form = PlayerFilterForm(request.GET or None)
            players = get_player_object_list(form)
            return render(
                request,
                "academy/players/partials/table_body.html",
                {"players": players},
            )

    return render(
        request,
        "partials/confirm_delete.html",
        {
            "instance": instance,
            "reverse_url": reverse("player-list"),
            "delete_view_name": "player-delete",
        },
    )


@login_required
def band_view(request, pk):
    instance = get_object_or_404(Band, pk=pk)
    return render(request, 'academy/view.html', {'instance': instance})

@login_required
def player_view(request, pk):
    instance = get_object_or_404(Player.all_objects, pk=pk)
    return render(request, 'academy/players/player_view.html', {'instance': instance})

@login_required
def championship_detail(request, pk):
    instance = get_object_or_404(Championship, pk=pk)
    return render(request, 'academy/championship/championship_detail.html', {'instance': instance})

@login_required
def championship_list(request):
    championships = Championship.objects.all().order_by('name')
    return render(request, 'academy/championship/championship_list.html', {'championships': championships})

@login_required
def championship_create(request):
    form_name = "Create Championship"
    if request.method == "POST":
        form = ChampionshipForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('championship-list')
    else:
        form = ChampionshipForm()
    return render(request, 'form.html', {'form': form, "form_name": form_name, 'list_url': reverse('championship-list'), })

@login_required
def championship_update(request, pk):
    form_name = "Update Championship"
    instance = get_object_or_404(Championship, pk=pk)
    if request.method == "POST":
        form = ChampionshipForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('championship-list')
    else:
        form = ChampionshipForm(instance=instance)
    return render(request, 'form.html', {'form': form, "form_name": form_name, 'list_url': reverse('championship-list'), })

@login_required
def championship_delete(request, pk):
    instance = get_object_or_404(Championship, pk=pk)
    if request.method == "POST":
        instance.delete()
        if request.htmx:
            championships = Championship.objects.all().order_by('name')
            return render(request, "academy/championship/partials/table_body.html", {"championships": championships})

    return render(
        request,
        "partials/confirm_delete.html",
        {"instance": instance, "reverse_url": reverse("championship-list"), "delete_view_name": "championship-delete"},
    )

@login_required
def rule_list(request):
    rules = Rule.objects.all().order_by('timestamp')
    return render(request, 'academy/rules/rule_list.html', {'rules': rules})

@login_required
def rule_create(request):
    form_name = "Create Rule"
    if request.method == "POST":
        form = RuleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('rule-list')
    else:
        form = RuleForm()
    return render(request, 'form.html', {'form': form, "form_name": form_name, 'list_url': reverse('rule-list'), })

@login_required
def rule_update(request, pk):
    form_name = "Update Rule"
    band = get_object_or_404(Rule, pk=pk)
    if request.method == "POST":
        form = RuleForm(request.POST, instance=band)
        if form.is_valid():
            form.save()
            return redirect('rule-list')
    else:
        form = RuleForm(instance=band)
    return render(request, 'form.html', {'form': form, "form_name": form_name, 'list_url': reverse('rule-list'), })

@login_required
def rule_delete(request, pk):
    instance = get_object_or_404(Rule, pk=pk)
    if request.method == "POST":
        instance.delete()
        if request.htmx:
            rules = Rule.objects.all().order_by("timestamp")
            return render(request, "academy/rules/partials/table_body.html", {"rules": rules})

    return render(
        request,
        "partials/confirm_delete.html",
        {"instance": instance, "reverse_url": reverse("rule-list"), "delete_view_name": "rule-delete"},
    )

@login_required
def rule_view(request, pk):
    instance = get_object_or_404(Rule, pk=pk)
    return render(request, 'academy/view.html', {'instance': instance})

@login_required
def auction_list(request):
    auctions = Auction.objects.all().order_by('-date')
    context = {
        'auctions': auctions
    }
    return render(request, 'academy/auctions/auction_list.html', context)
    
@login_required
def championship_history_list(request):
    championships = Championship.objects.prefetch_related("history__player")
    context = {
        'championships': championships
    }
    return render(request, 'academy/championship/championship_history.html', context)

@login_required
def hall_of_frame(request):
    players = Player.all_objects.filter(is_active=False)
    context = {
        'title': 'Hall Of Frame',
        'players': players
    }
    return render(request, "academy/players/player_image.html", context)

@login_required
def player_recall(request, pk):
    instance = get_object_or_404(Player.all_objects, pk=pk)
    if instance:
        instance.networth = 1000
        instance.is_active = True
        instance.save()
    return render(request, 'academy/players/player_view.html', {'instance': instance})