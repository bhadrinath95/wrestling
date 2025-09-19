import random
from academy.models import Championship
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

def generate_winner(match):
    print(match)
    
    if not match.winner:
        player_1 = match.player_1
        player_2 = match.player_2

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

        
        price_amount = (match.price_amount * 2/3)
        try:
            championship_obj = Championship.objects.get(player=winner)
            price_amount += price_amount * championship_obj.hike
        except Championship.DoesNotExist:
            pass

        winner.networth = winner.networth + price_amount
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
    return

def get_paginated_object_list(request, page_request_var, query_set, count):
    paginator = Paginator(query_set, count) 
    page = request.GET.get(page_request_var)
    try:
        query_set = paginator.page(page)
    except PageNotAnInteger:
        query_set = paginator.page(1)
    except EmptyPage:
        query_set = paginator.page(paginator.num_pages)
    return query_set