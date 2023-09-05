from enum import Enum, auto
from typing import NamedTuple
import logging


# Type Definitions
FrequencyParam = float  # Lambda parameter for Poisson distribution
CostParam = float       # Mean parameter for Normal distribution
MeanLoss = float        # Average loss per simulation
TotalLoss = float       # Total loss across all simulations
MedianLoss = float      # Median loss value
StdDevLoss = float      # Standard deviation of loss
MinLoss = float         # Minimum loss in simulations
MaxLoss = float         # Maximum loss in simulations
Percentile95Loss = float  # 95th percentile loss


class SimulationMetrics(NamedTuple):
    """
    NamedTuple to store various metrics that are calculated
    during the simulation of cyber risks.

    Attributes:
        total_loss (TotalLoss): Total loss during the simulation.
        mean_loss (MeanLoss): Mean loss during the simulation.
        median_loss (MedianLoss): Median loss during the simulation.
        std_dev_loss (StdDevLoss): Standard deviation of loss.
        min_loss (MinLoss): Minimum loss during the simulation.
        max_loss (MaxLoss): Maximum loss during the simulation.
        percentile_95_loss (Percentile95Loss): 95th percentile loss.
    """
    total_loss: TotalLoss
    mean_loss: MeanLoss
    median_loss: MedianLoss
    std_dev_loss: StdDevLoss
    min_loss: MinLoss
    max_loss: MaxLoss
    percentile_95_loss: Percentile95Loss


class RevenueBand(Enum):
    """
    Enum to represent different bands of revenue for companies.
    """
    BAND_10M = '10M'
    BAND_100M = '100M'
    BAND_500M = '500M'
    BAND_1B = '1B'
    
# Create a dictionary for constant-time lookup
revenue_band_dict = {band.value: band for band in RevenueBand}

def parse_revenue_band(band_str: str) -> RevenueBand:
    """
    Function to parse and return the corresponding RevenueBand Enum
    for a given revenue band string.

    Parameters:
        band_str (str): The string representation of a revenue band.

    Returns:
        RevenueBand: Enum representing the revenue band.
    """
    return revenue_band_dict.get(band_str, None)



class Industry(Enum):
    """
    Enum to represent different types of industries for companies.
    """
    HEALTHCARE = auto()  # 1
    FINANCE = auto()  # 2
    RETAIL = auto()  # 3
    MANUFACTURING = auto()  # 4
    CONSTRUCTION = auto()  # 5
    
    @classmethod
    def from_string(cls, industry_str: str):
        """
        Class method to parse and return the corresponding Industry Enum
        for a given industry string. Raises a ValueError if the input is invalid.

        Parameters:
            industry_str (str): The string representation of an industry.

        Returns:
            Industry: Enum representing the industry.

        Raises:
            ValueError: If the input string is not a valid industry.
        """
        try:
            return cls[industry_str.upper()]
        except KeyError:
            logging.error(f"Invalid industry string: {industry_str}")
            raise ValueError(f"Invalid industry string: {industry_str}")
