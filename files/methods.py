import pandas as pd
import numpy as np


def SPAV(ballots, seats: int):
    """Sequential Proportional Approvla Voting
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
    return remaining, seated


def uniform_price(weights, quota):
    """Returns the minimal amount of weight that can be taken uniformly
    from each voter such that the total amount taken is one quota."""
    if sum(weights) < quota:
        return float("inf")

    n = len(weights)
    sorted_weights = weights.sort_values()
    for w in sorted_weights:
        if quota / n < w:
            return quota / n
        quota -= w
        n -= 1
    return sorted_weights.values[-1]


def Allocated_Score(K, W, S):
    """Credit to https://electowiki.org/wiki/Allocated_Score
    Allocated Score is another name for STAR-PR
    """
    # Normalize score matrix
    ballots = pd.DataFrame(S.values / K, columns=S.columns)

    # Find number of voters and quota size
    V = ballots.shape[0]
    quota = V / W
    ballot_weight = pd.Series(np.ones(V), name="weights")

    # Populate winners in a loop
    winner_list = []
    while len(winner_list) < W:

        weighted_scores = ballots.multiply(ballot_weight, axis="index")

        # Select winner
        w = weighted_scores.sum().idxmax()

        # Add winner to list
        winner_list.append(w)

        # remove winner from ballot
        ballots.drop(w, axis=1, inplace=True)

        # Create lists for manipulation
        cand_df = pd.concat([ballot_weight, weighted_scores[w]], axis=1).copy()
        cand_df_sort = cand_df.sort_values(by=[w], ascending=False).copy()

        # find the score where a quota is filled
        split_point = cand_df_sort[cand_df_sort["weights"].cumsum() < quota][w].min()

        # Amount of ballot for voters who voted more than the split point
        spent_above = cand_df[cand_df[w] > split_point]["weights"].sum()

        # Allocate all ballots above split point
        if spent_above > 0:
            cand_df.loc[cand_df[w] > split_point, "weights"] = 0.0

        # Amount of ballot for voters who gave a score on the split point
        weight_on_split = cand_df[cand_df[w] == split_point]["weights"].sum()

        # Fraction of ballot on split needed to be spent
        if weight_on_split > 0:
            spent_value = (quota - spent_above) / weight_on_split

            # Take the spent value from the voters on the threshold evenly
            cand_df.loc[cand_df[w] == split_point, "weights"] = cand_df.loc[
                cand_df[w] == split_point, "weights"
            ] * (1 - spent_value)

        ballot_weight = cand_df["weights"].clip(0.0, 1.0)

    return winner_list


def MES(ballots, k):
    """Method of Equal Shares"""
    V = ballots.shape[0]
    quota = V / k
    weights = pd.Series(np.ones(V))

    seated = []
    while len(seated) < k:
        prices = ballots.drop(seated, axis=1).apply(
            lambda col: uniform_price(weights[col == 1], quota)
        )
        if prices.min() < float("inf"):
            w = prices.idxmin()
        else:  # default to largest remainders
            w = ballots.drop(seated, axis=1).mul(weights, axis=0).sum().idxmax()

        weights[ballots[w] == 1] = (
            weights[ballots[w] == 1].subtract(prices[w]).clip(0, 1)
        )
        seated.append(w)

    return seated


def STV(ballots, seats, quota):
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
