#!python3


"""
A utility for performing simulation experiments on auction mechanisms.
The experiment is similar to the one described by Gonen Segal-Halevi (2020).
In each experiment, we measure the actual vs. the optimal gain-from-trade.
This experiment using the real prices from Stock market. the prices are in csv files in stocks folder.

The results are printed to a CSV file. The columns are:

* stockname - the stock name that the results are relevant to it,
                currently it shows only the average of all stocks.
* recipe - [0, [1, None, 2, [3, None]]]
* numpossibletrades = n = total number of potential procurement-sets.
* optimalkmin = the k_min of the optimal trade. the minimum k of all recipes.
* optimalkmax = the k_max of the optimal trade. the maximum k of all recipes.
* gftformula = the least of gft ratio of the ascending-price mechanism.
* optimalcount = k =number of deals in the optimal trade, averaged over all iterations.
* optimalgft = OGFT = gain-from-trade in the optimal trade.
* auctioncount = k' = auction_count / optimal_count  * 100%.
* countratio = %k' = auction_count / optimal_count  * 100%.
* gft = GFT = gain-from-trade in the auction.
* gftratio = %GFT = gft / optimal_gft * 100%.
              Theoretically it should be at least (k-1)/(k+1).
              In the results, it is usually higher.

Author: AnonymousD
Since:  2020-08

"""

from markets import Market
from agents import AgentCategory

from tee_table.tee_table import TeeTable
from collections import OrderedDict
from get_stocks_data import getStocksPricesShuffled
from ascending_auction_recipetree_protocol import budget_balanced_ascending_auction
from recipetree import RecipeTree
import random


def experiment(results_csv_file: str, recipe: list, agent_counts: list, agent_values: list,
               nums_of_agents: list = None, num_of_iterations: int = 1, stocks_prices=None, stock_names=None):
    """
    Run an experiment similar to McAfee (1992) experiment on the given auction.
    :param agent_values: the values to multiple the values for each agent.
    :param agent_counts: the r_g counts of agents.
    :param num_of_iterations: number of iterations and calculate the mean of results.
    :param results_csv_file: the experiment result file.
    :param recipe: can be any vector of ones, e.g. (1,1,1), for our trade-reduction mechanism,
            or any vector of positive integers for our ascending-auction mechanism.
    :param nums_of_agents: list of n(s) for number of possible trades to make the calculations.
    :param stocks_prices: list of prices for each stock and each agent.
    :param stock_names: list of stocks names which prices are belongs, for naming only.
    """
    table_columns = ["stockname", "recipe", "numpossibletrades",
                     "optimalkmin", "optimalkmax", "gftratioformula",
                     "optimalcount", "optimalgft", "auctioncount", "auctionkmin", "auctionkmax",
                     "countratio", "kminratio", "kmaxratio","gft", "gftratio"]
    print('recipe:', recipe)
    results_table = TeeTable(table_columns, results_csv_file)
    recipe_str = str(recipe).replace(',', '-')
    recipe_size = len(agent_counts)
    if stocks_prices is None:
        (stocks_prices, stock_names) = getStocksPricesShuffled()
        #(stocks_prices, stock_names) = get_stocks_tree_prices(agent_counts, agent_values)

    if nums_of_agents is None:
        nums_of_agents = [10000000]
    total_results = {}
    for num_of_possible_ps in nums_of_agents:
        total_results[str(num_of_possible_ps)] = []
    for i in range(len(stock_names)):
        stock_prices = stocks_prices[i]
        for _ in range(num_of_iterations):
            last_iteration = False
            for num_of_possible_ps in nums_of_agents:
                while len(stock_prices) < num_of_possible_ps * recipe_size:
                    stock_prices = stock_prices + stock_prices
                random.shuffle(stock_prices)
                market = Market(
                    [AgentCategory("agent", [value * (-1 if j > 0 else 1)
                                             for value in stock_prices[j * num_of_possible_ps : (j+1) * num_of_possible_ps]])
                     for j in range(recipe_size)])
                recipe_tree = RecipeTree(market.categories, recipe)
                optimal_trade, optimal_count, optimal_gft, kmin, kmax = recipe_tree.optimal_trade_with_counters()
                # print('optimal trade:', optimal_trade, optimal_count, optimal_gft)
                auction_trade = budget_balanced_ascending_auction(market, recipe)
                auction_count = auction_trade.num_of_deals()
                auction_kmin = auction_trade.min_num_of_deals()
                auction_kmax = auction_trade.max_num_of_deals()
                gft = auction_trade.gain_from_trade()
                results = [("stockname", stock_names[i]),
                           ("recipe", recipe_str),
                           ("numpossibletrades", num_of_possible_ps),
                           ("optimalcount", optimal_count),
                           ("optimalkmin", kmin),
                           ("optimalkmax", kmax),
                           ("optimalgft", optimal_gft),
                           ("auctioncount", auction_count),
                           ("auctionkmin", auction_kmin),
                           ("auctionkmax", auction_kmax),
                           ("countratio", 0 if optimal_count == 0 else auction_count / optimal_count * 100),
                           ("kminratio", 0 if kmin == 0 else auction_kmin / kmin * 100),
                           ("kmaxratio", 0 if kmax == 0 else auction_kmax / kmax * 100),
                           ("gft", gft),
                           ("gftratio", 0 if optimal_gft == 0 else gft / optimal_gft * 100),
                           ("gftratioformula", 0 if kmin <= 1 else (kmin - 1) / kmin * 100)
                           ]
                # results_table.add(OrderedDict(results))
                if len(total_results[str(num_of_possible_ps)]) == 0:
                    total_results[str(num_of_possible_ps)] = results[0:len(results)]
                else:
                    sum_result = total_results[str(num_of_possible_ps)]
                    for index in range(len(results)):
                        if index > 2:
                            sum_result[index] = (results[index][0], sum_result[index][1] + results[index][1])
        print(stock_names[i], end=',')
    print()
    division_number = num_of_iterations * len(stock_names)
    for num_of_possible_ps in nums_of_agents:
        results = total_results[str(num_of_possible_ps)]
        #kmin = 0
        for index in range(len(results)):
            if 'gftratio' in results[index][0]:
                results[index] = (results[index][0], padding_zeroes(results[index][1] / division_number, 3))
            elif 'gft' in results[index][0]:
                results[index] = (results[index][0], padding_zeroes(results[index][1] / division_number, 1))
            elif index > 2:
                results[index] = (results[index][0], padding_zeroes(results[index][1] / division_number, 2))
            elif index == 0:
                results[index] = (results[index][0], 'Average')
            if results[index][0] == 'optimalkmin':
                kmin = results[index][1]
        #results.append(('gftformula', 0 if kmin <= 1 else (kmin - 1) / kmin * 100))
        results_table.add(OrderedDict(results))
    results_table.done()

def padding_zeroes(result, num_digits:int):
    str_result =  str(result) + ("0" * num_digits)
    return str_result[0 : str_result.index('.') + num_digits + 1]
