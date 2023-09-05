from typing import Tuple

import numpy as np

from .types import CostParam, FrequencyParam, MeanLoss, TotalLoss


def _get_industry_revenue_params(industry, revenue) -> Tuple[FrequencyParam, CostParam]:
    # TODO: implement mapping from industry and revenue to frequency and severity parameters

    raise NotImplementedError()


class CyberRiskSimulator:

    def __init__(self, industry: str, revenue: str):
        # TODO: add additional input parameter
        self.industry = industry
        self.revenue = revenue
        self.freq_param, self.sev_param = _get_industry_revenue_params(industry, revenue)

    def _simulate_attacks(self, num_simulations: int) -> np.ndarray:
        # TODO: simulate attacks based on Poisson distribution
        attack_counts = np.zeros(num_simulations)
        return attack_counts

    def _simulate_losses(self, attack_counts: np.ndarray) -> np.ndarray:
        # TODO: simulate losses based on severity distribution
        losses = np.zeros(len(attack_counts))
        return losses

    def run_simulation(self, num_simulations: int) -> Tuple[TotalLoss, MeanLoss]:
        attack_counts = self._simulate_attacks(num_simulations)
        losses = self._simulate_losses(attack_counts)
        total_loss = np.sum(losses)
        mean_loss = np.mean(losses)
        # TODO: add other metrics
        return total_loss, mean_loss
