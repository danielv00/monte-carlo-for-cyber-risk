import unittest
from unittest.mock import patch
from cyber_risk_simulator import CyberRiskSimulator, get_revenue_band_by_revenue, _get_industry_revenue_params  
from simulation_types import Industry, RevenueBand, SimulationMetrics
import numpy as np

class TestCyberRiskSimulator(unittest.TestCase):

    @patch('cyber_risk_simulator._get_industry_revenue_params')
    def test_init(self, mock_get_params):
        """
        Test initialization of CyberRiskSimulator class.
        """
        # Mock the return value of `_get_industry_revenue_params`
        mock_get_params.return_value = (0.3, 5.2)

        # Create a CyberRiskSimulator instance
        simulator = CyberRiskSimulator(Industry.HEALTHCARE, 100)

        # Assert instance attributes
        self.assertEqual(simulator.industry, Industry.HEALTHCARE)
        self.assertEqual(simulator.revenue, 100)
        self.assertEqual(simulator.num_simulations, 10_000)
        self.assertEqual(simulator.freq_param, 0.3)
        self.assertEqual(simulator.sev_param, 5.2)

    def test_get_revenue_band_by_revenue(self):
        """
        Test the function that maps revenue to a revenue band.
        """
        # Test various revenue amounts
        self.assertEqual(get_revenue_band_by_revenue(5), RevenueBand.BAND_10M)
        self.assertEqual(get_revenue_band_by_revenue(20), RevenueBand.BAND_100M)
        self.assertEqual(get_revenue_band_by_revenue(200), RevenueBand.BAND_500M)
        self.assertEqual(get_revenue_band_by_revenue(800), RevenueBand.BAND_1B)

    def test_get_revenue_band_by_revenue_negative(self):
        """
        Test for exception handling in revenue band mapping.
        """
        # Negative revenue should raise an error
        with self.assertRaises(ValueError):
            get_revenue_band_by_revenue(-1)

    @patch('cyber_risk_simulator.load_stats')
    def test_get_industry_revenue_params(self, mock_load_stats):
        """
        Test the extraction of frequency and severity parameters for given industry and revenue.
        """
        # Mock the stats for different revenue bands in the finance industry
        mock_load_stats.return_value = {
            'finance': {
                '10M': {'frequency': 5, 'cost': 1000},
                '100M': {'frequency': 10, 'cost': 2000},
                '500M': {'frequency': 15, 'cost': 3000},
                '1B': {'frequency': 20, 'cost': 4000},
            }
        }

        # Validate the returned frequency and severity parameters
        self.assertEqual(_get_industry_revenue_params(Industry.FINANCE, 5), (5, 1000))
        self.assertEqual(_get_industry_revenue_params(Industry.FINANCE, 20), (10, 2000))
        self.assertEqual(_get_industry_revenue_params(Industry.FINANCE, 200), (15, 3000))
        self.assertEqual(_get_industry_revenue_params(Industry.FINANCE, 800), (20, 4000))

    @patch('cyber_risk_simulator.poisson.rvs')
    @patch('cyber_risk_simulator.norm.rvs')
    @patch('cyber_risk_simulator._get_industry_revenue_params')
    def test_run_simulation(self, mock_get_params, mock_norm_rvs, mock_poisson_rvs):
        """
        Test running a cyber risk simulation and evaluating the resulting metrics.
        """
        # Mock various return values for functions used in the simulation
        mock_get_params.return_value = (0.3, 5.2)
        mock_poisson_rvs.return_value = np.array([1, 0, 2, 3, 1])
        mock_norm_rvs.return_value = 5.2

        # Create and run the simulator
        simulator = CyberRiskSimulator(Industry.HEALTHCARE, 100)
        metrics = simulator.run_simulation()

        # Validate the returned metrics
        self.assertIsInstance(metrics, SimulationMetrics)
        self.assertAlmostEqual(metrics.total_loss, 36.4)
        self.assertAlmostEqual(metrics.mean_loss, 7.28)
        self.assertAlmostEqual(metrics.median_loss, 5.2)
        self.assertAlmostEqual(metrics.min_loss, 0)
        self.assertAlmostEqual(metrics.max_loss, 15.6)

if __name__ == '__main__':
    unittest.main()
