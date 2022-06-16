import pandas as pd
import numpy as np
import pulp
from itertools import combinations, product


def additive_utility(ballots, winners):
    df = pd.DataFrame(ballots)
    numvoters = df.shape[0]
    return df[winners].sum().sum() / numvoters


def maximum_utility(ballots, winners):
    df = pd.DataFrame(ballots)
    numvoters = df.shape[0]
    return df[winners].max(axis=1).sum() / numvoters


def harmonic_utility(ballots, winners):
    df = pd.DataFrame(ballots)
    numvoters = df.shape[0]
    H = lambda x: sum(1 / i for i in range(1, x + 1))
    return df[winners].sum(axis=1).apply(H).sum() / numvoters


def exhaustive_optimal(ballots, seats, objective):
    val = 0
    df = pd.DataFrame(ballots)
    for wset in combinations(df.columns, seats):
        val = max(val, objective(ballots, list(wset)))
    return val


def justified_representation(ballots, winners):
    df = pd.DataFrame(ballots)
    numvoters = df.shape[0]
    return df.gt(df[winners].sum(axis=1), axis=0).sum().max() / numvoters


def maximin_support(ballots, winners):
    A = pd.DataFrame(ballots)[winners].to_numpy()
    numvoters = A.shape[0]
    seats = len(winners)

    model = pulp.LpProblem(sense=pulp.LpMaximize)

    s = pulp.LpVariable("s", lowBound=0)
    X = np.empty(A.shape, pulp.LpVariable)
    for i, j in product(range(numvoters), range(seats)):
        lpv = pulp.LpVariable(f"x{i}{j}", lowBound=0, upBound=A[i][j])
        X[i][j] = lpv

    for i in range(numvoters):
        model += pulp.lpSum(X[i]) <= 1

    Y = X.T
    for j in range(seats):
        model += pulp.lpSum(Y[j]) >= s

    model += s
    model.solve(pulp.PULP_CBC_CMD(msg=0))
    return pulp.value(s) / numvoters


def scrutinize_outcome(ballots, winners):
    df = pd.DataFrame(ballots)
    voters, cands = df.shape
    if cands > 20:
        print(
            f"Warning: this election contains {cands} candidates. "
            + "Some metrics may be slow to compute; consider eliminating unviable candidates from the ballots."
        )

    seats = len(winners)

    A = additive_utility(ballots, winners)
    A_ = exhaustive_optimal(ballots, seats, additive_utility)
    print(
        f"On average, voters approved {round(A, 2)} winners each, "
        + f"achieving {int((A/ A_)*100)}% of the best possible value."
    )

    B = maximum_utility(ballots, winners)
    B_ = exhaustive_optimal(ballots, seats, maximum_utility)
    print(
        f"Of all voters, {int(B*100)}% approved at least one winner, "
        + f"achieving {int((B / B_) * 100)}% of the best possible value."
    )

    C = harmonic_utility(ballots, winners)
    C_ = exhaustive_optimal(ballots, seats, harmonic_utility)
    print(
        f"The average harmonic utility was {round(C, 2)}, "
        + f"achieving {int((C / C_)*100)}% of the best possible value."
    )

    J = justified_representation(ballots, winners)
    t = "" if J >= voters / seats else " not"
    print(
        f"A coalition of {int(J*100)}% of voters were unsatisfied and approved "
        + f"the same candidate, which is{t} enough to destabilize a seat."
    )

    M = maximin_support(ballots, winners)
    print(
        (
            f"Assigning voters to winners in a balanced way, the least-supported winner represents {int(M*100)}% of the voters."
        )
    )


if __name__ == "__main__":
    ballots = [
        {"Red": 1, "Green": 0, "Yellow": 0, "Blue": 1, "Orange": 1},
        {"Red": 0, "Green": 1, "Yellow": 0, "Blue": 1, "Orange": 0},
        {"Red": 1, "Green": 0, "Yellow": 1, "Blue": 0, "Orange": 1},
        {"Red": 1, "Green": 0, "Yellow": 1, "Blue": 1, "Orange": 0},
        {"Red": 0, "Green": 1, "Yellow": 0, "Blue": 0, "Orange": 1},
        {"Red": 1, "Green": 0, "Yellow": 1, "Blue": 1, "Orange": 0},
        {"Red": 1, "Green": 1, "Yellow": 0, "Blue": 0, "Orange": 1},
        {"Red": 0, "Green": 1, "Yellow": 0, "Blue": 1, "Orange": 1},
        {"Red": 1, "Green": 0, "Yellow": 1, "Blue": 0, "Orange": 0},
    ]

    seated = ["Red", "Blue", "Yellow"]

    scrutinize_outcome(ballots, seated)
