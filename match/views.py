from django.shortcuts import render, get_object_or_404, redirect
from .models import SingleMatch
from .forms import SingleMatchForm, NotificationForm
from django.urls import reverse_lazy
from .utils import generate_winner
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from academy.models import Championship

# ---------- SINGLE MATCH VIEWS ----------
@login_required
def singlematch_list(request):
    matches = SingleMatch.objects.all().order_by('name')
    return render(request, 'matches/singlematch_list.html', {'matches': matches})

@login_required
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
        return redirect('singlematch_list')
    return render(request, 'confirm_delete.html', {'instance': instance, 'reverse_url': reverse('singlematch_list')})

@login_required
def singlematch_execute(request, pk):
    match = get_object_or_404(SingleMatch, pk=pk)
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