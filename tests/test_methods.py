from examples.ballot_generator import (
    generate_approval_ballots,
    generate_ranked_ballots,
    generate_score_ballots,
)
from examples.methods import SPAV, MES, STV, Allocated_Score, PAV
import numpy as np


def test_spav():
    ballots = generate_approval_ballots()

    elected = SPAV(ballots, seats=3)
    assert elected == ["C", "D", "B"]


def test_mes():
    ballots = generate_approval_ballots()

    elected = MES(ballots, 3)
    assert elected == ["C", "D", "B"]


def test_stv():
    ballots = generate_ranked_ballots()
    seats = 3
    quota = 1 + np.floor(len(ballots) / (seats + 1))

    assert (STV(ballots, seats, quota)) == ["D", "F", "B"]


def test_allocated_score():
    ballots = generate_score_ballots()

    elected = Allocated_Score(ballots, seats=3, max_score=5)
    assert elected == ["C", "D", "B"]


def test_pav():
    ballots = generate_approval_ballots()

    elected = PAV(ballots, seats=3)
    assert elected == ["B", "C", "D"]
