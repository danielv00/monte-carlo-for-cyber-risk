import numpy as np
import pandas as pd
import json
import datetime
from simulation_types import CostParam, FrequencyParam, MeanLoss, TotalLoss, RevenueBand, SimulationMetrics, revenue_band_dict, Industry
from typing import Tuple
from scipy.stats import poisson, norm
import logging
from config_setup import setup_config

# Load configuration data
config_dict = setup_config()

# Initialize a global variable to cache statistical data
stats_cache = None

def load_stats():
    '''Load statistical data from a JSON file into a global cache variable.'''
    global stats_cache
    if stats_cache is None:
        logging.debug('stats_cache is being reloaded')
        with open(config_dict['stats_csv'], 'r') as f:
            stats_cache = json.load(f)
    return stats_cache

def get_revenue_band_by_revenue(revenue: int) -> RevenueBand:
    '''
    Given a revenue value, this function returns the corresponding revenue band
    as an instance of the RevenueBand Enum.
    '''
    match revenue:
        case x if x < 0:
            logging.error(f"Invalid revenue: {revenue}")
            raise ValueError(f"Invalid revenue: {revenue}")
        case x if x <= 10:
            return RevenueBand.BAND_10M
        case x if x <= 100:
            return RevenueBand.BAND_100M
        case x if x <= 500:
            return RevenueBand.BAND_500M
        case x if x <= 1000:
            return RevenueBand.BAND_1B
        case _:
            logging.error(f"Invalid revenue: {revenue}")
            raise ValueError(f"Invalid revenue: {revenue}")
            
def get_revenue_boundaries_by_band(revenue_band: RevenueBand):
    '''
    Given a revenue band as an instance of the RevenueBand Enum,
    this function returns a tuple containing the lower and upper
    boundaries of that revenue band.
    '''
    logging.debug(f"get_revenue_boundaries_by_band: {revenue_band.value=}")
    match revenue_band:
        case RevenueBand.BAND_10M:
            return (0, 10)
        case RevenueBand.BAND_100M:
            return (10, 100)
        case RevenueBand.BAND_500M:
            return (100, 500)
        case RevenueBand.BAND_1B:
            return (500, 1000)
        case _:
            logging.error(f"Invalid revenue band: {revenue}")
            raise ValueError(f"Invalid revenue band: {revenue_band}")
            
            
def _get_industry_revenue_params(industry: Industry, revenue: float) -> Tuple[FrequencyParam, CostParam]:
    '''
    Retrieve frequency and cost parameters for a given industry and revenue.

    This method looks up a set of predefined statistical data for the provided industry and revenue,
    returning the corresponding frequency and cost parameters for that industry-revenue band.

    Parameters:
        industry (str): The industry to look up parameters for.
        revenue (float): The revenue for which to look up parameters. It will be used to determine
                         the revenue band within the provided industry.

    Returns:
        Tuple[FrequencyParam, CostParam]: A tuple containing frequency and cost parameters.

    Raises:
        ValueError: Raised if the industry is not found in the statistical data, or if the 
                    revenue band corresponding to the provided revenue is not found for the given industry.

    Notes:
        - The method uses the `load_stats` function to load statistical data.
        - The revenue is used to determine a revenue band using the `get_revenue_band_by_revenue` function.
    '''
    stats = load_stats()
    
    if industry.name.lower() not in stats:
        logging.error(f"Unknown industry: {industry}")
        raise ValueError(f"Unknown industry: {industry}")
    
    revenue_band = get_revenue_band_by_revenue(revenue)
    
    if revenue_band.value not in stats[industry.name.lower()]:
        logging.error(f"Invalid revenue band: {revenue_band} for industry: {industry}")
        raise ValueError(f"Invalid revenue band: {revenue_band} for industry: {industry}")
        
    frequency = stats[industry.name.lower()][revenue_band.value]['frequency']
    cost = stats[industry.name.lower()][revenue_band.value]['cost']
    
    return frequency, cost


class CyberRiskSimulator:
    '''
    A class to simulate cyber risk for a given industry and revenue.

    Attributes:
        industry (str): The industry category.
        revenue (float): The revenue value.
        num_simulations (int): Number of simulations to perform.
        freq_param (FrequencyParam): Frequency parameter for Poisson distribution.
        sev_param (CostParam): Severity parameter for normal distribution.
        results (DataFrame): A dataframe to store the results of the simulation.
    '''
    def __init__(self, industry: Industry, revenue: float, num_simulations: int = 10_000):
        '''Initialize CyberRiskSimulator with industry, revenue, and number of simulations.'''
        logging.debug(f'Init of CyberRiskSimulator with {industry=}, {revenue=}, {num_simulations=}')
        self.industry = industry
        self.revenue = revenue
        self.num_simulations = num_simulations
        self.freq_param, self.sev_param = _get_industry_revenue_params(industry, revenue)
        self.results = pd.DataFrame(columns=['simulation_id', 'attack_id', 'cost'])  # To store results

    def _simulate_attacks(self) -> np.ndarray:
        '''Simulate the number of attacks using a Poisson distribution.'''
        return poisson.rvs(self.freq_param, size=self.num_simulations)
 
    def _simulate_losses(self, attack_counts: np.ndarray) -> np.ndarray:
        '''
        Simulate the losses for a given number of attacks.

        Parameters:
            attack_counts (np.ndarray): The number of attacks for each simulation run.

        Returns:
            np.ndarray: Array containing the total loss for each simulation run.
        '''
        losses = np.zeros(len(attack_counts))
        data_to_append = []  # Accumulate data in this list
        
        # loop over all simulations
        for i, attack_count in enumerate(attack_counts):
            # loop over all attacks of the current simulation
            for attack_id in range(attack_count):
                cost = norm.rvs(self.sev_param, self.sev_param * 0.1)  # 10% std deviation
                data_to_append.append({
                    'simulation_id': i + 1,
                    'attack_id': attack_id + 1,
                    'cost': cost
                })
                losses[i] += cost
    
        self.results = pd.concat([self.results, pd.DataFrame(data_to_append)], ignore_index=True)
        
        return losses
 
    def _save_results_to_csv(self):
        '''Save the simulation results to a CSV file.'''
        logging.debug('saving simulation results of CyberRiskSimulator to csv')
        # Generate a timestamp string
        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Compose the filename
        filename = f"simulation_results_{timestamp_str}.csv"
        
        # Save to CSV
        self.results.to_csv(filename, index=False)
        
        
    def run_simulation(self, save_to_csv: bool = False) -> SimulationMetrics:
        '''
        Run the cyber risk simulation and optionally save the results to a CSV file.

        This method simulates the number of cyber attacks and the associated losses,
        computes various loss metrics across all simulations, and optionally saves
        these results to a CSV file.

        Parameters:
            save_to_csv (bool, optional): Whether to save the simulation results to a CSV file.
                                          Default is False.

        Returns:
            SimulationMetrics: A named tuple containing various loss metrics such as total loss, 
                               mean loss, median loss, standard deviation of losses, minimum loss, 
                               maximum loss, and the 95th percentile loss across all simulation runs.

        Metrics Included in SimulationMetrics:
            - total_loss: The total loss across all simulation runs.
            - mean_loss: The average loss per simulation run.
            - median_loss: The median loss across all simulation runs.
            - std_dev_loss: The standard deviation of losses across all simulation runs.
            - min_loss: The minimum loss observed across all simulation runs.
            - max_loss: The maximum loss observed across all simulation runs.
            - percentile_95_loss: The 95th percentile loss across all simulation runs.
        '''
        logging.debug('started run_simulation of CyberRiskSimulator')
        attack_counts = self._simulate_attacks()
        losses = self._simulate_losses(attack_counts)
        
        if save_to_csv:
            self._save_results_to_csv()
            
        # Compute metrics
        total_loss = np.sum(losses)
        mean_loss = np.mean(losses)
        median_loss = np.median(losses)
        std_dev_loss = np.std(losses)
        min_loss = np.min(losses)
        max_loss = np.max(losses)
        percentile_95_loss = np.percentile(losses, 95)


        return SimulationMetrics(
            total_loss=total_loss, 
            mean_loss=mean_loss,
            median_loss=median_loss,
            std_dev_loss=std_dev_loss,
            min_loss=min_loss,
            max_loss=max_loss,
            percentile_95_loss=percentile_95_loss)
