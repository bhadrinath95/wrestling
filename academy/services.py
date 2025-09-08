from itertools import combinations
import datetime
from academy.models import Band, Player
from match.models import SingleMatch

def create_league_matches():
    match_date = datetime.datetime(datetime.date.today().year, datetime.date.today().month, 30)
    bands = Band.objects.all()
    count = 1

    for band in bands:
        for gender in ['Male', 'Female']:
            players = Player.objects.filter(band=band, gender=gender)

            # Generate all unique matchups
            for p1, p2 in combinations(players, 2):
                SingleMatch.objects.create(
                    name=f"BWE Championship {band} Stage Match: {count}",
                    date=match_date,
                    player_1=p1,
                    player_2=p2,
                    winner=None,
                    price_amount=100,
                    entry_amount=50
                )
                count += 1