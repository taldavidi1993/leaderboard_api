import pytest
from pydantic import ValidationError
from main import ScoreEntry, create_or_update_score, get_user_rank, get_top_k, get_game_statistics  
import statistics

