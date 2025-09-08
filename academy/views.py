from django.shortcuts import render, get_object_or_404, redirect
from .models import Band, Player, Championship
from .forms import BandForm, PlayerForm, ChampionshipForm, PlayerFilterForm
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
        return redirect('band-list')
    return render(request, 'confirm_delete.html', {'instance': instance, 'reverse_url': reverse('band-list')})


@login_required
def player_list(request):
    form = PlayerFilterForm(request.GET or None)

    players = Player.objects.all().order_by("name")

    if form.is_valid():
        band = form.cleaned_data.get("band")
        gender = form.cleaned_data.get("gender")

        if band:
            players = players.filter(band=band)
        if gender:
            players = players.filter(gender=gender)

    return render(
        request,
        "academy/players/player_list.html",
        {"players": players, "form": form},
    )

@login_required
def player_images(request):
    form = PlayerFilterForm(request.GET or None)

    players = Player.objects.all().order_by("name")

    if form.is_valid():
        band = form.cleaned_data.get("band")
        gender = form.cleaned_data.get("gender")

        if band:
            players = players.filter(band=band)
        if gender:
            players = players.filter(gender=gender)

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
        return redirect('player-list')
    return render(request, 'confirm_delete.html', {'instance': instance, 'reverse_url': reverse('player-list')})

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
        return redirect('championship-list')
    return render(request, 'confirm_delete.html', {'instance': instance, 'reverse_url': reverse('championship-list')})
