#!python3


"""
A utility for performing simulation experiments on auction mechanisms.
The experiment is similar to the one described by Gonen Segal-Halevi (2020).
In each experiment, we measure the actual vs. the optimal gain-from-trade.
This experiment using the real prices from Stock market. the prices are in csv files in stocks folder.

The results are printed to a CSV file. The columns are:

* iterations - number of iterations to run the experiments and calculate the mean of the results.
* recipe - [0, [1, None, 2, [3, None]]]
* numofagents = n = total number of potential procurement-sets.
* meanoptimalcount = k =number of deals in the optimal trade, averaged over all iterations.
* meanoptimalkmin = the k_min of the optimal trade. the minimum k of all recipes.
* meanoptimalkmax = the k_max of the optimal trade. the maximum k of all recipes.
* gftformula = the least of gft ratio of the ascending-price mechanism.
* meanauctioncount = k' = auction_count.
* meanauctionkmin = k_min' = auction_count in min k' of all recipes.
* meanauctionkmax = k_max' = auction_count in mam k' of all recipes.
* countratio = %k' = auction_count / optimal_count  * 100%.
* meanoptimalgft = OGFT = gain-from-trade in the optimal trade.
* meanauctiontotalgft = GFT = gain-from-trade in the auction.
* totalgftratio = %GFT = gft / optimal_gft * 100%.
              Theoretically it should be at least (k-1)/(k+1).
              In the results, it is usually higher.

Author: AnonymousD
Since:  2020-08

"""

from markets import Market
from agents import AgentCategory

from tee_table.tee_table import TeeTable
from collections import OrderedDict
from tree_calculations import get_agents_analyze
from ascending_auction_recipetree_protocol import budget_balanced_ascending_auction
from recipetree import RecipeTree


def experiment(results_csv_file: str, recipe: list, value_ranges: list, nums_of_agents: list, num_of_iterations: int,
               agent_counts: list, agent_values: list):
    """
    Run an experiment similar to McAfee (1992) experiment on the given auction.
    :param agent_values: the list of multiple numbers for the agent values.
    :param agent_counts: the r_g from the paper.
    :param num_of_iterations: number of iterations to run the experiments and calculate the mean of the results.
    :param value_ranges: the ranges of random values of agents.
    :param results_csv_file: the experiment result file.
    :param recipe: can be any vector of ones, e.g. (1,1,1), for our trade-reduction mechanism,
            or any vector of positive integers for our ascending-auction mechanism.
    :param nums_of_agents: list of n(s) for number of possible trades to make the calculations.
    """
    table_columns = ["iterations", "recipe", "numofagents",
                     "meanoptimalcount", "meanoptimalkmin", "meanoptimalkmax", "gftformula",
                     "meanauctioncount", "meanauctionkmin", "meanauctionkmax", "countratio",
                     "kminauctionratio", "kmaxauctionratio",
                     "meanoptimalgft", "meanauctiontotalgft", "totalgftratio"]
    print('recipe:', recipe)
    results_table = TeeTable(table_columns, results_csv_file)
    recipe_str = str(recipe).replace(',', '-')
    for i in range(len(nums_of_agents)):
        sum_optimal_count = sum_auction_count = sum_optimal_kmin = sum_optimal_kmax = 0
        auction_count_kmin = auction_count_kmax = 0
        sum_optimal_gft = sum_auction_total_gft = 0
        for iteration in range(num_of_iterations):
            agents = []
            for category in range(len(agent_counts)):
                sign = 0 if category == 0 else 1
                agents.append(AgentCategory.uniformly_random("agent", int(nums_of_agents[i] * agent_counts[category]),
                                                             value_ranges[sign][0] * agent_values[category],
                                                             value_ranges[sign][1] * agent_values[category]))
            market = Market(agents)
            # print(agents)
            recipe_tree = RecipeTree(market.categories, recipe)
            optimal_trade, optimal_count, optimal_gft, kmin, kmax = recipe_tree.optimal_trade_with_counters()
            # print('optimal trade:', optimal_trade, optimal_count, optimal_gft)
            auction_trade = budget_balanced_ascending_auction(market, recipe)
            auction_count = auction_trade.num_of_deals()
            gft = auction_trade.gain_from_trade()
            sum_optimal_count += optimal_count
            sum_auction_count += auction_count

            sum_optimal_kmin += kmin
            sum_optimal_kmax += kmax
            auction_count_kmin += auction_trade.min_num_of_deals()
            auction_count_kmax += auction_trade.max_num_of_deals()

            sum_optimal_gft += optimal_gft
            sum_auction_total_gft += gft
        kmin_mean = sum_optimal_kmin / num_of_iterations
        results_table.add(OrderedDict([
            ("iterations", num_of_iterations),
            ("recipe", recipe_str),
            ("numofagents", nums_of_agents[i]),
            ("meanoptimalcount", padding_zeroes(sum_optimal_count / num_of_iterations,2)),
            ("meanoptimalkmin", padding_zeroes(kmin_mean,2)),
            ("meanoptimalkmax", padding_zeroes(sum_optimal_kmax / num_of_iterations,2)),
            ("gftformula", padding_zeroes((kmin_mean - 1) / kmin_mean * 100 if kmin_mean > 1 else 0,3)),
            ("meanauctioncount", padding_zeroes(sum_auction_count / num_of_iterations,2)),
            ("meanauctionkmin", padding_zeroes(auction_count_kmin / num_of_iterations,2)),
            ("meanauctionkmax", padding_zeroes(auction_count_kmax / num_of_iterations,2)),
            ("countratio", padding_zeroes(0 if sum_optimal_count == 0 else (sum_auction_count / sum_optimal_count) * 100,2)),
            ("kminauctionratio", padding_zeroes(0 if sum_optimal_kmin == 0 else (auction_count_kmin / sum_optimal_kmin) * 100,2)),
            ("kmaxauctionratio", padding_zeroes(0 if sum_optimal_kmax == 0 else (auction_count_kmax / sum_optimal_kmax) * 100,2)),
            ("meanoptimalgft", padding_zeroes(sum_optimal_gft / num_of_iterations,1)),
            ("meanauctiontotalgft", padding_zeroes(sum_auction_total_gft / num_of_iterations,1)),
            ("totalgftratio", padding_zeroes(0 if sum_optimal_gft == 0 else sum_auction_total_gft / sum_optimal_gft * 100,3))
        ]))
    results_table.done()

def padding_zeroes(result, num_digits:int):
    str_result = str(result)
    str_result += ("0" * num_digits) if '.' in str_result else '.' + ("0" * num_digits)
    return str_result[0 : str_result.index('.') + num_digits + 1]
