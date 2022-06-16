import pandas as pd
import numpy as np
from examples.proportionality_metrics import harmonic_utility, exhaustive_optimal
from itertools import combinations


def PAV(ballots: pd.DataFrame, seats: int):
    def H(x):
        return sum(1 / i for i in range(1, int(x) + 1))

    best_score = 0
    best_committee = None
    for wset in combinations(ballots.columns, seats):

        harmonic_score = ballots[list(wset)].sum(axis=1).map(H).sum()
        if harmonic_score > best_score:
            best_score, best_committee = harmonic_score, wset

    return list(best_committee)


def SPAV(ballots: pd.DataFrame, seats: int):
    """Sequential Proportional Approval Voting
    This system converts Approval Voting into a multi-round rule,
    selecting a candidate in each round and then reweighing the
    approvals for the subsequent rounds. The first candidate elected
    is the Approval winner (w1). The value of all ballots that
    approve of w1 are reduced in value from 1 to 1/2 and the
    approval scores recalculated. Next, the unelected candidate
    who has the highest approval score is elected (w2).
    Then the value of ballots that approve of both w1 and w2
    are reduced in value to 1/3, and the value of all ballots
    that approve of either w1 or w2 but not both are reduced in value to 1/2.
    """
    df = pd.DataFrame(ballots)
    seated = []
    while len(seated) < seats:
        weight = 1 / (1 + df[seated].sum(axis=1))
        remaining = df.drop(seated, axis=1).mul(weight, axis=0)
        seated.append(remaining.sum().idxmax())
    return seated


def uniform_price(weights, quota):
    """Returns the minimal amount of weight that can be taken uniformly
    from each voter such that the total amount taken is one quota."""
    if sum(weights) < quota:
        return float("inf")

    n = len(weights)
    sorted_weights = weights.sort_values()
    for weight in sorted_weights:
        if quota / n < weight:
            return quota / n
        quota -= weight
        n -= 1
    return sorted_weights.values[-1]


def Allocated_Score(ballots: pd.DataFrame, seats: int, max_score: int):
    """Credit to https://electowiki.org/wiki/Allocated_Score
    Allocated Score is another name for STAR-PR

    Parameters:

    """
    # Normalize score matrix
    ballots = pd.DataFrame(ballots.values / max_score, columns=ballots.columns)

    # Find number of voters and quota size
    voters = ballots.shape[0]
    quota = voters / seats
    ballot_weight = pd.Series(np.ones(voters), name="weights")

    # Populate winners in a loop
    winner_list = []
    while len(winner_list) < seats:

        weighted_scores = ballots.multiply(ballot_weight, axis="index")

        # Select winner
        winner = weighted_scores.sum().idxmax()

        # Add winner to list
        winner_list.append(winner)

        # remove winner from ballot
        ballots.drop(winner, axis=1, inplace=True)

        # Create lists for manipulation
        cand_df = pd.concat([ballot_weight, weighted_scores[winner]], axis=1).copy()
        cand_df_sort = cand_df.sort_values(by=[winner], ascending=False).copy()

        # find the score where a quota is filled
        split_point = cand_df_sort[cand_df_sort["weights"].cumsum() < quota][
            winner
        ].min()

        # Amount of ballot for voters who voted more than the split point
        spent_above = cand_df[cand_df[winner] > split_point]["weights"].sum()

        # Allocate all ballots above split point
        if spent_above > 0:
            cand_df.loc[cand_df[winner] > split_point, "weights"] = 0.0

        # Amount of ballot for voters who gave a score on the split point
        weight_on_split = cand_df[cand_df[winner] == split_point]["weights"].sum()

        # Fraction of ballot on split needed to be spent
        if weight_on_split > 0:
            spent_value = (quota - spent_above) / weight_on_split

            # Take the spent value from the voters on the threshold evenly
            cand_df.loc[cand_df[winner] == split_point, "weights"] = cand_df.loc[
                cand_df[winner] == split_point, "weights"
            ] * (1 - spent_value)

        ballot_weight = cand_df["weights"].clip(0.0, 1.0)

    return winner_list


def MES(ballots: pd.DataFrame, seats: int):
    """Method of Equal Shares"""
    V = ballots.shape[0]
    quota = V / seats
    weights = pd.Series(np.ones(V))

    seated = []
    while len(seated) < seats:
        prices = ballots.drop(seated, axis=1).apply(
            lambda col: uniform_price(weights[col == 1], quota)
        )
        if prices.min() < float("inf"):
            winner = prices.idxmin()
        else:  # default to largest remainders
            winner = ballots.drop(seated, axis=1).mul(weights, axis=0).sum().idxmax()

        weights[ballots[winner] == 1] = (
            weights[ballots[winner] == 1].subtract(prices[winner]).clip(0, 1)
        )
        seated.append(winner)

    return seated


def STV(ballots: pd.DataFrame, seats: int, quota: int):
    """Single Transferable Vote
    Instant Runoff Voting, proportionally.
    """
    V, C = ballots.shape

    weights = np.ones(V)
    elected = []
    remaining = list(ballots.columns)

    for _ in range(seats):
        y = ballots.max(axis=1)
        y = pd.concat([y] * len(remaining), axis=1).rename(
            columns=lambda i: ballots.columns[i]
        )
        fp = y == ballots
        support = fp.mul(weights, axis=0).sum(axis=0)

        while support.max() < quota and len(remaining) > seats - len(elected):
            remaining.remove(support.idxmin())
            ballots = ballots[remaining]

            y = ballots.max(axis=1)
            y = pd.concat([y] * len(remaining), axis=1).rename(
                columns=lambda i: ballots.columns[i]
            )
            fp = y == ballots
            support = fp.mul(weights, axis=0).sum(axis=0)

        winner = support.idxmax()
        surplus = max(1, support.max() / quota)
        weights[fp[winner]] *= 1 - 1 / surplus

        elected.append(winner)
        remaining.remove(winner)
        ballots = ballots[remaining]

    return elected
