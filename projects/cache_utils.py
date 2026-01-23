# projects/cache_utils.py
from django.core.cache import cache

def invalidate_board_cache(board_id):
    # brute-force pattern delete (acceptable at this scale)
    for key in cache.iter_keys(f"board_detail:{board_id}:*"):
        cache.delete(key)
