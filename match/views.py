from django.shortcuts import render, get_object_or_404, redirect
from .models import SingleMatch, Tournament
from .forms import SingleMatchForm, NotificationForm, TournamentForm, CreateLeagueForm, CreateMatchSetupForm, ChampionshipChallengeForm, PlayerSelectionFilterForm
from django.urls import reverse_lazy
from .utils import generate_winner, get_paginated_object_list
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from academy.models import Championship
from django.db.models import Case, When, Value, IntegerField
import datetime
from academy.models import Band, Player
from itertools import combinations
from django.db.models import Count
from django.db import transaction
from django.db.models import Q
from datetime import timedelta
from django.utils.timezone import now


def create_match(player1, player2, name, tournament, price_amount, entry_amount, match_date):
    """Helper to create match and generate winner."""
    match = SingleMatch.objects.create(
        name=name,
        date=match_date,
        tournament=tournament,
        player_1=player1,
        player_2=player2,
        winner=None,
        price_amount=price_amount,
        entry_amount=entry_amount
    )
    generate_winner(match)
    return match

def generate_tournament_winner(tournament, price_amount, entry_amount, match_date, count):
    while True:
        player_wins = (
            Player.objects
            .filter(single_match_winner__tournament=tournament)
            .annotate(wins_count=Count("single_match_winner"))
            .order_by("-wins_count")
        )

        max_wins = player_wins.first().wins_count
        top_players = list(player_wins.filter(wins_count=max_wins))

        if len(top_players) == 1:
            return
        
        with transaction.atomic():
            for p1, p2 in combinations(top_players, 2):
                create_match(
                    player1=p1,
                    player2=p2,
                    name=f"Top Round Match {count}: {p1.name} vs {p2.name}",
                    tournament=tournament,
                    price_amount=price_amount,
                    entry_amount=entry_amount,
                    match_date=match_date
                )
                count += 1
    return

@login_required
def tournament_list(request):
    tournaments = Tournament.objects.all().order_by("is_completed", "is_main_tournament", "-date", "-updated_at")
    return render(request, 'matches/tournament/tournament_list.html', {'tournaments': tournaments})

@login_required
def tournament_complete(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    tournament.is_completed = True
    tournament.save()
    return redirect('tournament_list')

@login_required
def tournament_detail(request, pk):
    
    tournament = get_object_or_404(Tournament, pk=pk)
    matches = SingleMatch.objects.filter(tournament=tournament).order_by("-updated_at")

    player_wins = (
        Player.objects
        .filter(single_match_winner__tournament=tournament) 
        .annotate(wins_count=Count("single_match_winner"))
        .order_by("-wins_count")
    )

    top_players = []
    if player_wins.exists():
        max_wins = player_wins.first().wins_count
        top_players = player_wins.filter(wins_count=max_wins)

    return render(
        request,
        "matches/singlematch/singlematch_list.html",
        {
            "tournament": tournament,
            "matches": matches,
            "top_players": top_players,
        },
    )

@login_required
def tournament_create(request):
    form_name = "Create Tournament"
    if request.method == 'POST':
        form = TournamentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tournament_list')
    else:
        form = TournamentForm()
    return render(request, 'form.html', {'form': form, "form_name": form_name, 'list_url': reverse('tournament_list'), })

@login_required
def tournament_match_setup(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    form_name = f"Create Match for Tournament - {tournament.name}"

    # --- Player filtering form ---
    filter_form = PlayerSelectionFilterForm(request.GET or None)
    players_qs = Player.objects.all().order_by("-winningpercentage")

    if filter_form.is_valid():
        players_qs = filter_form.filter_queryset(players_qs)

    # --- Match setup form (restricted queryset) ---
    form = CreateMatchSetupForm()
    form.fields["players"].queryset = players_qs

    if request.method == "POST":
        form = CreateMatchSetupForm(request.POST)
        form.fields["players"].queryset = players_qs  # must reset here too
        if form.is_valid():
            players = form.cleaned_data.get("players")
            price_amount = form.cleaned_data.get("price_amount") or 0
            entry_amount = form.cleaned_data.get("entry_amount") or 0
            match_name = form.cleaned_data.get("match_name")

            match_date = datetime.date.today()
            count = 1

            with transaction.atomic():
                for p1, p2 in combinations(players, 2):
                    create_match(
                        player1=p1,
                        player2=p2,
                        name=f"{match_name} Match {count}",
                        tournament=tournament,
                        price_amount=price_amount,
                        entry_amount=entry_amount,
                        match_date=match_date,
                    )
                    count += 1
            generate_tournament_winner(tournament, price_amount, entry_amount, match_date, count)
            return redirect("tournament_list")

    return render(
        request,
        "matches/tournament/tournament_match_setup_form.html",
        {
            "form": form,
            "form_name": form_name,
            "filter_form": filter_form,
            "list_url": reverse("tournament_list"),
        },
    )


@login_required
def tournament_create_league(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    form_name = f"Create League for '{tournament.name}'"

    if request.method == 'POST':
        form = CreateLeagueForm(request.POST)
        if form.is_valid():
            gender = form.cleaned_data.get("gender")
            bands = form.cleaned_data.get("bands")
            price_amount = form.cleaned_data.get("price_amount") or 0
            entry_amount = form.cleaned_data.get("entry_amount") or 0

            match_date = datetime.date.today()
            count = 1

            with transaction.atomic():
                for band in bands:
                    players = Player.objects.filter(band=band)
                    if gender != "Both":
                        players = players.filter(gender=gender)

                    for p1, p2 in combinations(players, 2):
                        create_match(
                            player1=p1,
                            player2=p2,
                            name=f"{band.name} Stage Match: {count}",
                            tournament=tournament,
                            price_amount=price_amount,
                            entry_amount=entry_amount,
                            match_date=match_date
                        )
                        count += 1
            generate_tournament_winner(tournament, price_amount, entry_amount, match_date, count)
            return redirect('tournament_list')

    else:
        form = CreateLeagueForm()

    return render(
        request,
        'form.html',
        {
            'form': form,
            'form_name': form_name,
            'list_url': reverse('tournament_list'),
        }
    )

@login_required
def tournament_update(request, pk):
    form_name = "Update Tournament"
    tournament = get_object_or_404(Tournament, pk=pk)
    if request.method == 'POST':
        form = TournamentForm(request.POST, instance=tournament)
        if form.is_valid():
            form.save()
            return redirect('tournament_list')
    else:
        form = TournamentForm(instance=tournament)
    return render(request, 'form.html', {'form': form, "form_name": form_name, 'list_url': reverse('tournament_list'), })

@login_required
def tournament_delete(request, pk):
    instance = get_object_or_404(Tournament, pk=pk)
    if request.method == 'POST':
        instance.delete()
        if request.htmx:
                tournaments = Tournament.objects.all().order_by("-updated_at")
                return render(request, "matches/tournament/partials/table_body.html", {"tournaments": tournaments})
    return render(
        request,
        "partials/confirm_delete.html",
        {"instance": instance, "reverse_url": reverse("tournament_list"), "delete_view_name": "tournament_delete"},
    )

def get_single_match_object_list():
    return (
        SingleMatch.objects
        .annotate(
            is_unfinished=Case(
                When(winner__isnull=True, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        )
    ).order_by("is_unfinished", "-updated_at")

@login_required
def singlematch_list(request):
    query = request.GET.get("q")
    matches = get_single_match_object_list()
    if query:
        matches = matches.search(query)
    page_request_var = 'page'
    matches = get_paginated_object_list(request, page_request_var, matches, 25)
    context = {
        'tournament': None, 
        "page_request_var": page_request_var, 
        'matches': matches
        }
    return render(request, 'matches/singlematch/singlematch_list.html', context)

@login_required
def singlematch_detail(request, pk):
    match = get_object_or_404(SingleMatch, pk=pk)
    notifications = match.match_notification.all().order_by("timestamp")

    return render(
        request,
        'matches/singlematch/singlematch_detail.html',
        {
            'match': match,
            'notifications': notifications
        }
    )

@login_required
def singlematch_create(request):
    form_name = "Create Single Match"
    if request.method == 'POST':
        form = SingleMatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('singlematch_list')
    else:
        form = SingleMatchForm()
    return render(request, 'form.html', {'form': form, "form_name": form_name, 'list_url': reverse('singlematch_list'), })

@login_required
def singlematch_update(request, pk):
    form_name = "Update Single Match"
    match = get_object_or_404(SingleMatch, pk=pk)
    if request.method == 'POST':
        form = SingleMatchForm(request.POST, instance=match)
        if form.is_valid():
            form.save()
            return redirect('singlematch_detail', pk=match.pk)
    else:
        form = SingleMatchForm(instance=match)
    return render(request, 'form.html', {'form': form, "form_name": form_name, 'list_url': reverse('singlematch_list'), })

@login_required
def singlematch_delete(request, pk):
    instance = get_object_or_404(SingleMatch, pk=pk)
    if request.method == 'POST':
        instance.delete()
        if request.htmx:
            matches = get_single_match_object_list()
            page_request_var = 'page'
            matches = get_paginated_object_list(request, page_request_var, matches, 25)
            context = {
                'tournament': None, 
                "page_request_var": page_request_var, 
                'matches': matches
                }
            return render(
                request,
                "matches/singlematch/partials/table_body.html",
                context
            )
    return render(request, 'partials/confirm_delete.html', {'instance': instance, 'reverse_url': reverse('singlematch_list'), "delete_view_name": "singlematch_delete"})

@login_required
def singlematch_execute(request, pk):
    match = get_object_or_404(SingleMatch, pk=pk)
    generate_winner(match)
    return redirect('singlematch_detail', pk=match.pk)

@login_required
def singlematch_complete_all_matches(request):
    matches = SingleMatch.objects.filter(winner=None, tournament__is_main_tournament=False)
    with transaction.atomic():
        for match in matches:
            generate_winner(match)
    return redirect('singlematch_list')

@login_required
def create_notification(request, pk):
    form_name = "Create Notification"
    match = get_object_or_404(SingleMatch, pk=pk)

    if request.method == "POST":
        form = NotificationForm(request.POST)
        if form.is_valid():
            notification = form.save(commit=False)
            notification.match = match
            notification.save()
            return redirect('singlematch_detail', pk=match.pk)
    else:
        form = NotificationForm()

    return render(
        request,
        'form.html',
        {'form': form, "form_name": form_name, 'list_url': reverse('singlematch_list'), }
    )

@login_required
def upcoming_main_tournament(request):
    seven_days_ago = now().date() - timedelta(days=7)

    tournament = (
        Tournament.objects
        .filter(is_main_tournament=True, is_completed=False)
        .filter(date__gte=seven_days_ago)
        .order_by("date")
        .first()
    )

    championship_freeze = False
    days_until = None

    if tournament:
        days_until = (tournament.date - now().date()).days - 7
        if days_until < 0:
            championship_freeze = True

    matches = SingleMatch.objects.filter(tournament=tournament)

    # Dropdown list of all completed main tournaments
    completed_tournaments = Tournament.objects.filter(
        is_main_tournament=True
    ).order_by("-date")

    # If this is an HTMX request (for a selected tournament)
    if request.headers.get("HX-Request"):
        tournament_id = request.GET.get("tournament_id")
        tournament = get_object_or_404(Tournament, pk=tournament_id)
        matches = SingleMatch.objects.filter(tournament=tournament)
        return render(
            request,
            "matches/tournament/partials/tournament_details_partial.html",
            {
                "tournament": tournament,
                "matches": matches,
                "championship_freeze": championship_freeze,
                "days_until": days_until,
            },
        )

    context = {
        "tournament": tournament,
        "matches": matches,
        "championship_freeze": championship_freeze,
        "days_until": days_until,
        "completed_tournaments": completed_tournaments,
    }

    return render(request, "matches/tournament/upcoming_main.html", context)

@login_required
def challenge_for_championship(request, player_id):
    challenger = get_object_or_404(Player, pk=player_id)  # Top player in this tournament

    if request.method == "POST":
        form = ChampionshipChallengeForm(request.POST)
        if form.is_valid():
            championship = form.cleaned_data['championship']
            match = SingleMatch.objects.create(
                name=form.cleaned_data['name'],
                date=form.cleaned_data['date'],
                tournament=form.cleaned_data['tournament'],
                player_1=championship.player,
                player_2=challenger,
                winner=None,
                price_amount=form.cleaned_data['price_amount'],
                entry_amount=form.cleaned_data['entry_amount'],
                is_championship_match=True
            )
            return redirect("singlematch_detail", pk=match.pk)
    else:
        form = ChampionshipChallengeForm()

    return render(
        request,
        "matches/singlematch/challenge_form.html",
        {
            "form": form,
            "challenger": challenger
        },
    )