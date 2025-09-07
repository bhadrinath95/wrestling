from django.shortcuts import render, get_object_or_404, redirect
from .models import SingleMatch
from .forms import SingleMatchForm, NotificationForm
from django.urls import reverse_lazy
import random
from django.urls import reverse

# ---------- SINGLE MATCH VIEWS ----------

def singlematch_list(request):
    matches = SingleMatch.objects.all()
    return render(request, 'matches/singlematch_list.html', {'matches': matches})

def singlematch_detail(request, pk):
    match = get_object_or_404(SingleMatch, pk=pk)
    notifications = match.match_notification.all().order_by("timestamp")

    return render(
        request,
        'matches/singlematch_detail.html',
        {
            'match': match,
            'notifications': notifications
        }
    )

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

def singlematch_delete(request, pk):
    instance = get_object_or_404(SingleMatch, pk=pk)
    if request.method == 'POST':
        instance.delete()
        return redirect('singlematch_list')
    return render(request, 'confirm_delete.html', {'instance': instance, 'reverse_url': reverse('singlematch_list')})

def singlematch_execute(request, pk):
    match = get_object_or_404(SingleMatch, pk=pk)

    if not match.winner:
        player_1 = match.player_1
        player_2 = match.player_2

        if not player_1 or not player_2:
            return redirect('singlematch_detail', pk=match.pk)

        # Get winning percentages (default 50 if missing)
        p1_win_percent = getattr(player_1, "winning_percentage", 50)
        p2_win_percent = getattr(player_2, "winning_percentage", 50)

        total = p1_win_percent + p2_win_percent
        if total == 0:
            p1_skill_prob = p2_skill_prob = 0.5
        else:
            p1_skill_prob = p1_win_percent / total
            p2_skill_prob = p2_win_percent / total

        # Random factor
        rand_val = random.random()
        p1_rand_prob = rand_val
        p2_rand_prob = 1 - rand_val

        # Final probability
        p1_final_prob = (p1_skill_prob * 0.2) + (p1_rand_prob * 0.8)
        p2_final_prob = (p2_skill_prob * 0.2) + (p2_rand_prob * 0.8)

        total_prob = p1_final_prob + p2_final_prob
        p1_final_prob /= total_prob
        p2_final_prob /= total_prob

        # Pick winner
        winner = player_1 if random.random() < p1_final_prob else player_2
        loser = player_2 if winner == player_1 else player_1

        # Save to match
        match.winner = winner
        match.save()

        winner.networth = winner.networth + (match.price_amount * 2/3)
        winner.matchesplayed += 1
        winner.wins += 1
        winner.save()

        winner_band = winner.band
        winner_band.networth = winner_band.networth + (match.price_amount * 1/3)
        winner_band.save()

        loser.networth = loser.networth - (match.entry_amount * 2/3)
        loser.matchesplayed += 1
        loser.save()

        loser_band = loser.band
        loser_band.networth = loser_band.networth - (match.entry_amount * 1/3)
        loser_band.save()

    return redirect('singlematch_list')

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