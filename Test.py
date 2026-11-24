"""
Runs cleaning robot experiments using Max-Plus and Random agents.
Saves simulation and individual robot statistics to CSV files.
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

# Experimental configurations for both coordination methods.
TESTS = [
    {"name": "max plus 1 agent", "method": "maxplus",
     "numAgents": 1, "width": 30, "height": 20,
     "nDirty": 100, "maxSteps": 500, "repetitions": 100},

    {"name": "max plus 2 agents", "method": "maxplus",
     "numAgents": 2, "width": 30, "height": 20,
     "nDirty": 100, "maxSteps": 500, "repetitions": 100},

    {"name": "max plus 4 agents", "method": "maxplus",
     "numAgents": 4, "width": 30, "height": 20,
     "nDirty": 100, "maxSteps": 500, "repetitions": 100},

    {"name": "max plus 8 agents", "method": "maxplus",
     "numAgents": 8, "width": 30, "height": 20,
     "nDirty": 100, "maxSteps": 500, "repetitions": 100},

    {"name": "max plus 16 agents", "method": "maxplus",
     "numAgents": 16, "width": 30, "height": 20,
     "nDirty": 100, "maxSteps": 500, "repetitions": 100},

    {"name": "random 1 agent", "method": "random",
     "numAgents": 1, "width": 30, "height": 20,
     "nDirty": 100, "maxSteps": 500, "repetitions": 100},

    {"name": "random 2 agents", "method": "random",
     "numAgents": 2, "width": 30, "height": 20,
     "nDirty": 100, "maxSteps": 500, "repetitions": 100},

    {"name": "random 4 agents", "method": "random",
     "numAgents": 4, "width": 30, "height": 20,
     "nDirty": 100, "maxSteps": 500, "repetitions": 100},

    {"name": "random 8 agents", "method": "random",
     "numAgents": 8, "width": 30, "height": 20,
     "nDirty": 100, "maxSteps": 500, "repetitions": 100},

    {"name": "random 16 agents", "method": "random",
     "numAgents": 16, "width": 30, "height": 20,
     "nDirty": 100, "maxSteps": 500, "repetitions": 100}
]

OUTPUT_FILE = "test_results.csv"
AGENT_OUTPUT_FILE = "agent_results.csv"

COLUMNS = [
    "test", "run", "seed", "numAgents", "width", "height",
    "nDirty", "maxSteps", "executionTime", "completionTime",
    "cleanedPercentage", "remainingDirtyCells", "totalMoves",
    "allClean", "runTimeS"
]

AGENT_COLUMNS = [
    "test", "run", "seed", "numAgents", "agentId",
    "activeSteps", "movements", "cellsCleaned"
]

# Runs one simulation and collects its statistics.
# Parameters: 
#   test: Experimental configuration dictionary.
#   run: Repetition number.
#   seed: Random seed used for reproducibility.
# Returns: Simulation statistics and individual robot statistics.
def runTest(test, run, seed):
    startTime = time.perf_counter()

    model = CleaningModel(
        maxSteps=test["maxSteps"],
        numAgents=test["numAgents"],
        width=test["width"],
        height=test["height"],
        nDirty=test["nDirty"],
        agentType=test["method"],
        seed=seed
    )

    while model.running:
        model.step()

    runTime = time.perf_counter() - startTime

    row = {
        "test": test["name"],
        "run": run,
        "seed": seed,
        "numAgents": test["numAgents"],
        "width": test["width"],
        "height": test["height"],
        "nDirty": test["nDirty"]
    }

    row.update(model.getStats())
    row["runTimeS"] = round(runTime, 6)

    agentRows = []

    for agentStats in model.getAgentStats():
        agentRow = {
            "test": test["name"],
            "run": run,
            "seed": seed,
            "numAgents": test["numAgents"],
        }

        agentRow.update(agentStats)
        agentRows.append(agentRow)

    return row, agentRows


# Runs all experimental configurations and repetitions.
# Parameters: 
#   tests: List of experimental configurations.
# Returns: Simulation summaries and individual robot statistics.
def runAll(tests):
    summaries = []
    agentRows = []

    for test in tests:
        for run in range(1, test["repetitions"] + 1):
            seed = test.get("seedStart", 0) + run - 1

            row, robots = runTest(test, run, seed)

            summaries.append(row)
            agentRows.extend(robots)

        print(
            f"Test '{test['name']}' completed "
            f"({test['repetitions']} runs)"
        )

    return summaries, agentRows


# Saves experiment results into a CSV file.
# Parameters: 
#   rows: List of result dictionaries.
#   path: Output filename.
#   columns: Column names for the CSV file.
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
    summaries, agentRows = runAll(TESTS)

    saveCsv(summaries, OUTPUT_FILE, COLUMNS)
    saveCsv(agentRows, AGENT_OUTPUT_FILE, AGENT_COLUMNS)


if __name__ == "__main__":
    main()