"""
Runs 100 simulations per configuration and saves them in one log
(test_results.csv, one row per simulation).
Authors: Adriana Sandoval Santos - A01667445
         Marbella Barba De los Santos - A01660946
         Javier Padilla Marcial - A01660945
         Camila Quintanilla Cabrera - A01662397
         Alani Daniel Garcia Maya - A01277308
Date: 2026-11-21
"""

import csv
import time
from Model import CleaningModel

AGENT_COUNTS = [1, 2, 4, 8, 16]

# The two methods compared: coordinated Max-Plus robots and the random
# robots of Activity M1.
METHODS = [
    {"name": "max plus", "label": "Max-Plus", "method": "maxplus"},
    {"name": "random", "label": "Random (M1)", "method": "random"},
]

# Creates the configuration of one test.
# Parameters: method: One entry of METHODS; numAgents: Number of robots.
# Returns: Dictionary with the test configuration.
def makeTest(method, numAgents):
    agentWord = "agent" if numAgents == 1 else "agents"

    return {
        "name": f"{method['name']} {numAgents} {agentWord}",
        "label": method["label"],
        "method": method["method"],
        "numAgents": numAgents,
        "width": 30, "height": 20,
        "maxSteps": 500, "repetitions": 100,
    }

TESTS = [
    makeTest(method, numAgents)
    for method in METHODS
    for numAgents in AGENT_COUNTS
]

# Optional keys per test: "seedStart" (first seed, default 0) and
# "startAtOrigin" (True: all robots start at [1,1]; default False).

OUTPUT_FILE = "test_results.csv"

COLUMNS = [
    "test", "method", "run", "seed", "numAgents", "width", "height",
    "maxSteps", "executionTime", "completionTime",
    "cleanedPercentage", "remainingDirtyCells", "totalMoves",
    "allClean", "runTimeS"
]

# Runs one simulation and collects its statistics.
# Parameters: test: Configuration; run: Run number; seed: Random seed.
# Returns: Dictionary with the statistics of the simulation.
def runTest(test, run, seed):
    startTime = time.perf_counter()

    model = CleaningModel(
        maxSteps=test["maxSteps"],
        numAgents=test["numAgents"],
        width=test["width"],
        height=test["height"],
        nDirty=100,
        agentType=test["method"],
        startAtOrigin=test.get("startAtOrigin", False),
        seed=seed,
    )

    while model.running:
        model.step()

    runTime = time.perf_counter() - startTime

    row = {
        "test": test["name"],
        "method": test["label"],
        "run": run,
        "seed": seed,
        "numAgents": test["numAgents"],
        "width": test["width"],
        "height": test["height"],
    }

    row.update(model.getStats())
    row["runTimeS"] = round(runTime, 6)

    return row

# Runs all configurations and repetitions.
# Parameters: tests: List of experimental configurations.
# Returns: List with one statistics row per simulation.
def runAll(tests):
    summaries = []

    for test in tests:
        for run in range(1, test["repetitions"] + 1):
            seed = test.get("seedStart", 0) + run - 1

            row = runTest(test, run, seed)

            summaries.append(row)

        print(
            f"Test '{test['name']}' completed "
            f"({test['repetitions']} runs)"
        )

    return summaries

# Saves simulation results into a CSV file.
# Parameters: rows: Data to save; path: Output filename.
# columns: CSV column names.
# Returns: None.
def saveCsv(rows, path, columns):
    with open(path, "w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    print("CSV saved on", path)

# Runs the experiments and saves their results.
# Parameters: None.
# Returns: None.
def main():
    summaries = runAll(TESTS)
    saveCsv(summaries, OUTPUT_FILE, COLUMNS)

if __name__ == "__main__":
    main()