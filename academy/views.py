from django.shortcuts import render, get_object_or_404, redirect
from .models import Band, Player, Championship, Rule
from .forms import BandForm, PlayerForm, ChampionshipForm, PlayerFilterForm, RuleForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required

def home_view(request):
    return render(request, 'base.html', {})

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
        band = form.cleaned_data.get("band")
        gender = form.cleaned_data.get("gender")
        sort_by = form.cleaned_data.get("sort_by")

        if band:
            players = players.filter(band=band)
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
        {"players": players, "form": form},
    )

@login_required
def player_images(request):
    form = PlayerFilterForm(request.GET or None)
    players = get_player_object_list(form)
    return render(
        request,
        "academy/players/player_image.html",
        {"players": players, "form": form},
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
def player_update(request, pk):
    form_name = "Update Player"
    player = get_object_or_404(Player, pk=pk)
    if request.method == "POST":
        form = PlayerForm(request.POST, instance=player)
        if form.is_valid():
            form.save()
            return redirect('player-list')
    else:
        form = PlayerForm(instance=player)
    return render(request, 'form.html', {'form': form, "form_name": form_name, 'list_url': reverse('player-list'), })

@login_required
def player_delete(request, pk):
    instance = get_object_or_404(Player, pk=pk)
    if request.method == "POST":
        instance.delete()
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
        {"instance": instance, "reverse_url": reverse("player-list"), "delete_view_name": "player-delete"},
    )


@login_required
def band_view(request, pk):
    instance = get_object_or_404(Band, pk=pk)
    return render(request, 'academy/view.html', {'instance': instance})

@login_required
def player_view(request, pk):
    instance = get_object_or_404(Player, pk=pk)
    return render(request, 'academy/view.html', {'instance': instance})

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