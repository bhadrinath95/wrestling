from django.contrib import admin
from .models import SingleMatch, Player


class PlayerAdmin(admin.ModelAdmin):
    search_fields = ("name",)   # Required for autocomplete_fields to work

class SingleMatchAdmin(admin.ModelAdmin):
    list_display = ("name", "player_1", "player_2", "winner", "price_amount", "entry_amount")
    search_fields = ("name", "player_1__name", "player_2__name", "winner__name")
    list_filter = ("price_amount", "entry_amount")
    autocomplete_fields = ("player_1", "player_2", "winner")


# Register all models
admin.site.register(Player, PlayerAdmin)
admin.site.register(SingleMatch, SingleMatchAdmin)
