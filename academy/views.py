from django.shortcuts import render, get_object_or_404, redirect
from .models import Band, Player
from .forms import BandForm, PlayerForm
from django.urls import reverse

# ----------------- BAND CRUD -----------------
def home_view(request):
    return render(request, 'base.html', {})

def band_list(request):
    bands = Band.objects.all().order_by('name')
    return render(request, 'academy/bands/band_list.html', {'bands': bands})

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

def band_delete(request, pk):
    instance = get_object_or_404(Band, pk=pk)
    if request.method == "POST":
        instance.delete()
        return redirect('band-list')
    return render(request, 'confirm_delete.html', {'instance': instance, 'reverse_url': reverse('band-list')})


# ----------------- PLAYER CRUD -----------------
def player_list(request):
    players = Player.objects.all().order_by('name')
    return render(request, 'academy/players/player_list.html', {'players': players})

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

def player_delete(request, pk):
    instance = get_object_or_404(Player, pk=pk)
    if request.method == "POST":
        instance.delete()
        return redirect('player-list')
    return render(request, 'confirm_delete.html', {'instance': instance, 'reverse_url': reverse('player-list')})

def band_view(request, pk):
    instance = get_object_or_404(Band, pk=pk)
    return render(request, 'academy/view.html', {'instance': instance})

def player_view(request, pk):
    instance = get_object_or_404(Player, pk=pk)
    return render(request, 'academy/view.html', {'instance': instance})