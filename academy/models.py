from django.db import models
from django.db.models.signals import pre_save, post_save

# Create your models here.
class Band(models.Model):
    name = models.CharField(max_length=200)
    networth = models.FloatField(default=0)
    image_url = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return self.name

class Player(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Others', 'Others'),
    ]

    name = models.CharField(max_length=200)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    band = models.ForeignKey(Band, on_delete=models.CASCADE, related_name='player_band')
    wins = models.PositiveIntegerField(default=0)
    matchesplayed = models.PositiveIntegerField(default=0)
    winningpercentage = models.FloatField(default=0)
    networth = models.FloatField(default=0)
    image_url = models.CharField(max_length=120, null=True, blank=True)


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