from itertools import combinations
import datetime
from academy.models import Band, Player
from match.models import SingleMatch
from match.utils import generate_winner

def create_league_matches():
    # ["Green Bands", "Hand Bands", "Red Bands", "White Bands", "Yellow Bands"]
    # ["NXT Generations Band"]
    # ["Female", "Male"]
    INCLUDE_BANDS = ["NXT Generations Band"]
    GENDER_LIST = ["Male"]
    PRICE_AMOUNT = 200
    ENTRY_AMOUNT = 100
    MATCH_NAME = "NXT Championship Sept'25"
    
    match_date = datetime.datetime(datetime.date.today().year, datetime.date.today().month, 30)
    bands = Band.objects.filter(name__in=INCLUDE_BANDS)
    count = 1

    for band in bands:
        for gender in GENDER_LIST:
            players = Player.objects.filter(band=band, gender=gender)

            # Generate all unique matchups
            for p1, p2 in combinations(players, 2):
                SingleMatch.objects.create(
                    name=f"{MATCH_NAME} {band} Stage Match: {count}",
                    date=match_date,
                    player_1=p1,
                    player_2=p2,
                    winner=None,
                    price_amount=PRICE_AMOUNT,
                    entry_amount=ENTRY_AMOUNT
                )
                count += 1

def complete_all_matches():
    matches = SingleMatch.objects.filter(winner=None)
    for match in matches:
        generate_winner(match)
    return

def add_certain_amount_to_players():
    AMOUNT = 1000
    players = Player.objects.all()
    for player in players:
        player.networth += AMOUNT
        player.save()

def add_certain_amount_to_bands():
    AMOUNT = 10000
    bands = Band.objects.all()
    for band in bands:
        band.networth += AMOUNT
        band.save()