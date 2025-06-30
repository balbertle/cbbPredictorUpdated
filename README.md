# Stochastic College Basketball Game Simulator

This simulator primarily uses stochastic processes through Markov Chain matrices to simulate a college basketball game and backtests the results using Monte Carlo Simulations.

This is an updated version that, instead of relying on a single metric, implements a log5 balancing system to blend team and opponent statistics for the probabilities in the main stochastic process. A Pythagorean expectation formula was derived to inform a portion of the total winning simulation, with backtesting used to find the optimal exponents for each season. A BARTHAG percentage was also used for a small weight.

---

## Key Features

* **Monte Carlo Simulation:** Runs the full 64-team tournament bracket a specified number of times to find the most probable winner for every potential matchup.
* **Advanced Blended Prediction Model:** Each game's outcome is determined by a weighted average of three distinct statistical models:
    1.  **Possession-by-Possession Simulation (Log5 Sim):** A detailed, bottom-up model that simulates every possession of a game using a Markov chain. It contains states like turnovers, 2-point vs. 3-point shots, shooting fouls, and offensive rebounds.
    2.  **Pythagorean Expectation:** A high-level, top-down model that predicts win probability based on a team's adjusted offensive and defensive efficiency ratings. The exponent is derived from backtesting through the season and finding the exponent with the least error.
    3.  **BARTHAG Power Rating:** A power rating from barttorvik.com that estimates a team's probability of beating an average Top-25 team. This provides a third, independent measure of team strength.
* **Data:** The model is powered by two distinct data sources:
    * A primary CSV file (`cbb25.csv`) from https://www.kaggle.com/datasets/andrewsundberg/college-basketball-dataset which is scraped from barttorvik.com.
    * A CSV file scraped from Basketball Reference with custom stats.
* **Bracket Visualization:** After all simulations are complete, the script generates a clean, hierarchical bracket visualization.

---

## Stats

I made two stochastic simulators. One, in `bayseian.py`, uses BARTHAG for most of the weighting and achieved ~88% accuracy. My main, more realistic simulator applies a log5 balancing system. While this version is less accurate, it is more realistic in its approach.

## Mathematical Models Explained

The base of the simulator comes from blending three distinct mathematical models. The final win probability for any given game is a weighted average of the probabilities from each model.

P(final) = (P(log5) * w + (pythag) * w + P(barthag) * w(barthag))

Where w represents the user-defined weight for each model.

### 1. Possession-by-Possession Simulation (Markov Chain)

This is the most detailed, bottom-up model. It treats a basketball possession as a series of discrete states (e.g., 'Start', 'Make 2', 'Turnover', 'Offensive Rebound'). The simulation progresses by moving from state to state based on calculated probabilities.

* **Concept:** A Markov Chain where the probability of the next state depends only on the current state.
* **Implementation:** A transition matrix T is created for each team, where the element T(ij) is the probability of moving from state i to state j. For example, from the 'Start' state, a team might have a 15% chance of a 'Turnover', a 45% chance of a '2-Point Shot Attempt', etc. These probabilities are calculated from raw team statistics and adjusted for the opponent's defensive prowess.
* **Outcome (P(log5)):** The simulation runs thousands of full games, possession by possession. The win probability is simply the number of times a team wins divided by the total number of simulations.

P(log5) = (Number of Simulated Wins)/(Total Number of Simulations)

### 2. Pythagorean Expectation

This is a high-level model developed by Bill James that estimates a team's win percentage based on the number of points they score versus the number of points they allow.

* **Formula:** The expected win percentage is given by:
    Win% = (Points For)^k / ((Points For)^k + (Points Against)^k)
* **Exponent (k):** The exponent k is empirically derived to best fit the sport. For this model, the optimal exponent for college basketball (around 4.386 for 2024/25 season) is calculated by finding the value that minimizes the error between the expected and actual win percentages across the entire league.
* **Matchup Adaptation (P(pythag)):** To predict a single game between Team A and Team B, we first estimate the points each would score against the other's defense, using their adjusted efficiency ratings (`ADJOE`, `ADJDE`):
    `Score_A = (ADJOE_A * ADJDE_B) / LeagueAvgEfficiency`
    `Score_B = (ADJOE_B * ADJDE_A) / LeagueAvgEfficiency`

    The win probability for Team A is then:
        `P_pythag(A) = (Score_A)^k / ((Score_A)^k + (Score_B)^k)`

### 3. BARTHAG Power Rating (Log5 Method)

This model uses the `BARTHAG` rating—a measure of a team's chance to beat an average Top-25 team—to predict the outcome of a head-to-head matchup using the Log5 formula.

* **Concept:** The Log5 formula gives the probability that Team A will win against Team B, given their individual probabilities of winning against an average opponent.
* **Formula (P(barthag)):** Let P(A) be the BARTHAG rating for Team A, and P(B) be the rating for Team B. The probability of A winning is:
    `P_barthag(A) = (P(A) - P(A) * P(B)) / (P(A) + P(B) - 2 * P(A) * P(B))`

By blending these three distinct approaches—a granular simulation, an efficiency-based expectation, and a power rating comparison—the model produces a more robust and nuanced prediction than any single method could alone.

---

## File Structure

The project is not very organized, I apologize. I have a weighted and unweighted simulator:

* `marchmadness2025log5.py`: The main executable script which runs the log5 based simulator.
* `log5sim.py`: The core simulation engine. It contains the `simulate_matchup` function which implements the blended model logic.
* `prepare_stats.py`: The crucial bridge between the raw data sources and the simulation engine. It calculates true, normalized per-possession event probabilities.
* `/helpers`: Folder that contains utility functions for loading data, such as `getTeams()` from the CSV.
* `cbb25.csv`: The primary data file containing team statistics and advanced ratings.

---

## Setup & Installation

### 1. Prerequisites

* Python 3.6 or higher.
* `cbb25.csv` file from Kaggle or other year.

### 2. Required Libraries

This project requires the following Python libraries. You can install them using pip:

```bash
pip install numpy networkx matplotlib