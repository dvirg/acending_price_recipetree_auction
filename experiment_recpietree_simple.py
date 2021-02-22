#!python3

"""
Simulation experiment for our IJCAI 2021 paper, with recipes that are vectors of ones.
With using stock market real data and random values.

Since:  2020-08
Author: AnonymousD

"""

import experiment_ascending_auction_recipetree_stock

import experiment_ascending_auction_recipetree_random
from os.path import join

results_file = join("results", "experiment_recipetree_simple_5000")

nums_of_agents = [2, 4, 6, 10, 16, 26, 50, 100, 500, 1000, 2000, 5000]

print("\n\n###### TEST MULTI RECIPE AUCTION WITH A SINGLE PATH: [1,1,1]")

iterations = 1000
recipe_paper_example = [0, [1, None, 2, [3, None]]]
recipes = [recipe_paper_example]

run_random = False #True
for recipe in recipes:
    if run_random:
        experiment_ascending_auction_recipetree_random.experiment(results_file + "_random.csv",
                                                                  recipe=recipe,
                                                                  value_ranges=[(1, 1000), (-1000, -1)],
                                                                  nums_of_agents=nums_of_agents,
                                                                  num_of_iterations=iterations,
                                                                  agent_counts=[1, 1, 1, 1],
                                                                  agent_values=[1, 1, 1, 1]
                                                                  )

    else:
        #if run_random:
        experiment_ascending_auction_recipetree_stock.experiment(results_file + "_stock.csv", recipe=recipe,
                                                                 agent_counts=[1, 1, 1, 1],
                                                                 agent_values=[1, 1, 1, 1],
                                                                 nums_of_agents=nums_of_agents,
                                                                 num_of_iterations=iterations
                                                                 )
