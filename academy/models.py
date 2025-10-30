from django.db import models
from django.db.models.signals import pre_save, post_save
from django.utils.timezone import now

# Create your models here.
class Band(models.Model):
    name = models.CharField(max_length=200)
    networth = models.FloatField(default=0)
    image_url = models.CharField(max_length=120, null=True, blank=True)
    emoji = models.CharField(max_length=5, null=True, blank=True)

    def __str__(self):
        return self.name
    
    @property
    def men_count(self):
        return self.player_band.filter(gender='Male').count()
    
    @property
    def women_count(self):
        return self.player_band.filter(gender='Female').count()
    
    @property
    def player_count(self):
        return self.player_band.count()
    
    @property
    def matchesplayed(self):
        return self.player_band.aggregate(total=models.Sum('matchesplayed'))['total'] or 0
    
    @property
    def wins(self):
        return self.player_band.aggregate(total=models.Sum('wins'))['total'] or 0
    
    @property
    def winningpercentage(self):
        matches = self.matchesplayed
        wins = self.wins
        return round((wins / matches) * 100, 2) if matches > 0 else 0

class ActivePlayerManager(models.Manager):
    def get_queryset(self):
        # Override to filter only active players
        return super().get_queryset().filter(is_active=True)
    
class Player(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    name = models.CharField(max_length=200, unique=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    band = models.ForeignKey(Band, on_delete=models.CASCADE, related_name='player_band')
    wins = models.PositiveIntegerField(default=0)
    matchesplayed = models.PositiveIntegerField(default=0)
    winningpercentage = models.FloatField(default=0)
    networth = models.FloatField(default=0)
    image_url = models.CharField(max_length=120, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    objects = ActivePlayerManager()
    all_objects = models.Manager()

    spouse = models.OneToOneField(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="partner"
    )

    def __str__(self):
        return self.name
    
def object_pre_save(sender, instance, *args, **kwargs):
    instance.winningpercentage = (instance.wins / instance.matchesplayed) * 100 if instance.matchesplayed else 0

def player_post_save(sender, instance, *args, **kwargs):
    spouse = instance.spouse
    if spouse and spouse.spouse != instance:
        spouse.spouse = instance
        spouse.save()

pre_save.connect(object_pre_save, sender=Player) 
post_save.connect(player_post_save, sender=Player)

class Championship(models.Model):
    name = models.CharField(max_length=200)
    player = models.OneToOneField(Player, on_delete=models.CASCADE, null=True, blank=True)
    image_url = models.CharField(max_length=120, null=True, blank=True)
    hike = models.FloatField()
    updated_on = models.DateTimeField(auto_now=True) 

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

_old_players = {}

def cache_old_player(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Championship.objects.get(pk=instance.pk)
            _old_players[instance.pk] = old.player
        except Championship.DoesNotExist:
            _old_players[instance.pk] = None


def create_championship_history(sender, instance, created, **kwargs):
    old_player = _old_players.pop(instance.pk, None)
    new_player = instance.player

    if created:
        # New championship with player
        if new_player:
            ChampionshipHistory.objects.create(
                championship=instance,
                player=new_player,
                started_on=instance.updated_on,
            )
    else:
        if old_player != new_player:
            # End old player's reign
            if old_player:
                ChampionshipHistory.objects.filter(
                    championship=instance,
                    player=old_player,
                    ended_on__isnull=True
                ).update(ended_on=now())

            # Start new player's reign
            if new_player:
                ChampionshipHistory.objects.create(
                    championship=instance,
                    player=new_player,
                    started_on=instance.updated_on,
                )

pre_save.connect(cache_old_player, sender=Championship) 
post_save.connect(create_championship_history, sender=Championship)

    
class ChampionshipHistory(models.Model):
    championship = models.ForeignKey(Championship, on_delete=models.CASCADE, related_name="history")
    player = models.ForeignKey("Player", on_delete=models.CASCADE)
    started_on = models.DateTimeField()
    ended_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_on"]

    @property
    def duration(self):
        end_time = self.ended_on or now()
        return end_time - self.started_on

    def __str__(self):
        return f"{self.championship.name} - {self.player} ({self.started_on.date()} to {self.ended_on.date() if self.ended_on else 'Present'})"
    
class Rule(models.Model):
    name = models.CharField(max_length=200)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.name
    
class Auction(models.Model):
    player = models.ForeignKey("Player", on_delete=models.CASCADE, related_name="auctions")
    from_band = models.ForeignKey("Band", on_delete=models.SET_NULL, null=True, blank=True, related_name="auctions_from")
    to_band = models.ForeignKey("Band", on_delete=models.SET_NULL, null=True, blank=True, related_name="auctions_to")
    price = models.FloatField()  # player's networth used in auction
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Auction: {self.player.name} from {self.from_band} → {self.to_band} for {self.price}"
