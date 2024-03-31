# ncaat_conference_outcomes
Analysis and simulation of conference outcomes in NCAA tournament

This repo analyzes the question of whether performance of teams from the same conference is correlated in the NCAA tournament. For more commentary, see the companion piece at https://kaleidoscopemind.substack.com/.

The core analysis is in `notebooks/analysis.ipynb`, but it depends on a simulation that's most of the code and frankly most of the interesting part. 

How to replicate: 
1. Run `python -m scripts.get_trank_data` to download all the raw data used in the analysis (from barttorvik.com)

If all you want to do is run the first two sections of the analysis (empirical data), you can jump to the last step. If not, you'll need to run the simulation: 
2. Run `notebooks/prep-seed-advancement.ipynb` and `notebooks/prep-tourney-teams.ipynb` to prep inputs to the simulation
3. Run `python -m scripts.simulate_tournaments` to simulate historical NCAA tournaments with advancement randomly determined by seedline. 
    - Note that the default (1000 sims per season) takes about 20 minutes on my (moderately powered) machine. If you want to reduce the number of sims, add an argument like `--simulations=100` 

4. Run `notebooks/analysis.ipynb` to see results of analysis.