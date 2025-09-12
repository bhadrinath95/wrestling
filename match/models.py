from django.db import models
from academy.models import Player
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models import Q

# Create your models here.
class Tournament(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateField()

    def __str__(self):
        return self.name
    
class SingleMatchQuerySet(models.QuerySet):
    def search(self, query=None):
        if query is None or query == "":
            return self.none()
        lookups = (
            Q(name__icontains=query) |
            Q(player_1__name__icontains=query) |
            Q(player_2__name__icontains=query) |
            Q(winner__name__icontains=query) |
            Q(player_1__band__name__icontains=query) |
            Q(player_2__band__name__icontains=query) |
            Q(tournament__name__icontains=query)
        )
        return self.filter(lookups) 

class SingleMatchManager(models.Manager):
    def get_queryset(self):
        return SingleMatchQuerySet(self.model, using=self._db)

    def search(self, query=None):
        return self.get_queryset().search(query=query)

class SingleMatch(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateField()
    tournament = models.ForeignKey(Tournament, on_delete=models.SET_NULL, null=True, blank=True, related_name="tournament")
    player_1 = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name="single_match_player_1")
    player_2 = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name="single_match_player_2")
    winner = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name="single_match_winner")
    price_amount = models.FloatField(default=0)
    entry_amount = models.FloatField(default=0)
    updated_at = models.DateTimeField(auto_now=True) 

    objects = SingleMatchManager()

    def __str__(self):
        return f"{self.name} - {self.player_1} vs {self.player_2}"
    
class Notification(models.Model):
    match = models.ForeignKey(SingleMatch, on_delete=models.CASCADE, related_name="match_notification")

    content = models.TextField()
    image_url = models.CharField(max_length=120, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=False,auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.match}"