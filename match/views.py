from django.shortcuts import render, get_object_or_404, redirect
from .models import SingleMatch, Tournament
from .forms import SingleMatchForm, NotificationForm, TournamentForm, CreateLeagueForm, CreateMatchSetupForm
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
from django.utils.timezone import now


# ---------- TOURNAMENT MATCH VIEWS ----------
@login_required
def tournament_list(request):
    tournaments = Tournament.objects.all().order_by("is_completed", "is_main_tournament", "-updated_at")
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

    # Count wins per player in this tournament
    player_wins = (
        Player.objects
        .filter(single_match_winner__tournament=tournament)   # winner FK -> Player
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
    form_name = f"Create Match  for Tournament- {tournament.name}"
    form = CreateMatchSetupForm()

    if request.method == "POST":
        form = CreateMatchSetupForm(request.POST)
        if form.is_valid():
            players = form.cleaned_data.get("players")
            price_amount = form.cleaned_data.get("price_amount") or 0
            entry_amount = form.cleaned_data.get("entry_amount") or 0
            match_name = form.cleaned_data.get("match_name")

            match_date = datetime.date.today()
            count = 1

            for p1, p2 in combinations(players, 2):
                SingleMatch.objects.create(
                    name=f"{match_name} Match {count}",
                    date=match_date,
                    tournament=tournament,
                    player_1=p1,
                    player_2=p2,
                    winner=None,
                    price_amount=price_amount,
                    entry_amount=entry_amount,
                )
                count += 1

            return redirect("tournament_list")

    return render(
        request,
        "matches/tournament/tournament_match_setup_form.html",
        {
            "form": form,
            "form_name": form_name,
            "list_url": reverse("tournament_list"),
        },
    )


@login_required
def tournament_create_league(request, pk):
    form_name = "Create League"
    tournament = get_object_or_404(Tournament, pk=pk)
    if request.method == 'POST':
        form = CreateLeagueForm(request.POST)
        if form.is_valid():

            gender = form.cleaned_data.get("gender")
            bands = form.cleaned_data.get("bands")
            price_amount = form.cleaned_data.get("price_amount") or 0
            entry_amount = form.cleaned_data.get("entry_amount") or 0

            match_date = datetime.date.today()
            count = 1

            for band in bands:
                if gender == "Both":
                    players = Player.objects.filter(band=band)
                else:
                    players = Player.objects.filter(band=band, gender=gender)
                for p1, p2 in combinations(players, 2):
                    SingleMatch.objects.create(
                        name=f"{band.name} Stage Match: {count}",
                        date=match_date,
                        tournament=tournament,
                        player_1=p1,
                        player_2=p2,
                        winner=None,
                        price_amount=price_amount,
                        entry_amount=entry_amount
                    )
                    count += 1

            return redirect('tournament_list')
    else:
        form = CreateLeagueForm()
    return render(
        request,
        'form.html',
        {
            'form': form,
            "form_name": form_name,
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

# ---------- SINGLE MATCH VIEWS ----------
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
    return redirect('singlematch_list')

@login_required
def singlematch_complete_all_matches(request):
    matches = SingleMatch.objects.filter(winner=None, tournament__is_main_tournament=False)
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
    tournament = (
        Tournament.objects
        .filter(is_main_tournament=True, is_completed=False, date__gte=now().date())
        .order_by("date")
        .first()
    )
    matches = SingleMatch.objects.filter(tournament=tournament)
    context = {
        "tournament": tournament,
        "matches": matches
    }
    return render(request, "matches/tournament/upcoming_main.html", context)