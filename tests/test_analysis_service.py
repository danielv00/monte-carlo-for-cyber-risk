import unittest
from unittest.mock import patch
import pandas as pd
from analysis_service import AnalysisService
from simulation_types import Industry, SimulationMetrics

'''
The database methods are mocked using unittest.mock.patch to isolate the unit tests from the database.
Calls to random number generation functions are also mocked to generate predictable outputs for testing.
The CyberRiskSimulator class is mocked to isolate the AnalysisService class methods during testing.
The setUp method sets up a DataFrame of synthetic company data that will be used in multiple tests.
'''

class TestAnalysisService(unittest.TestCase):

    def setUp(self):
        """
        Setup for tests.
        """
        self.test_data = pd.DataFrame({
            'company_id': [1, 2],
            'revenue_usd': [10, 20],
            'industry': ['finance', 'healthcare']
        })
        self.test_data['revenue_usd'] = self.test_data['revenue_usd'].astype('int32')

    @patch('analysis_service.sqlite3.connect')
    def test_generate_synthetic_companies(self, mock_db_connect):
        """
        Test _generate_synthetic_companies method.
        """
        with patch('analysis_service.np.random.uniform') as mock_uniform, \
             patch('analysis_service.np.random.choice') as mock_choice:

            # Mocking the random generation methods
            mock_uniform.return_value = [10, 20]
            mock_choice.return_value = ['finance', 'healthcare']

            service = AnalysisService(num_companies=2)

            # Assert that the companies DataFrame was correctly generated
            pd.testing.assert_frame_equal(service.companies, self.test_data)
        
            # Assert that the database connection was called
            mock_db_connect.assert_called()

    @patch('analysis_service.sqlite3.connect')
    def test_save_synthetic_companies_to_db(self, mock_db_connect):
        """
        Test _save_synthetic_companies_to_db method.
        """
        service = AnalysisService(num_companies=2)
        service._save_synthetic_companies_to_db(self.test_data)
        mock_db_connect.assert_called()

    @patch('analysis_service.sqlite3.connect')
    def test_save_simulation_to_db(self, mock_db_connect):
        """
        Test _save_simulation_to_db method.
        """
        service = AnalysisService(num_companies=2)
        service._save_simulation_to_db(self.test_data)
        mock_db_connect.assert_called()

    @patch('analysis_service.CyberRiskSimulator.run_simulation')
    @patch('analysis_service.CyberRiskSimulator.__init__')
    def test_run_simulations(self, mock_simulator_init, mock_run_simulation):
        """
        Test run_simulations method.
        """
        mock_simulator_init.return_value = None  # Mocking the constructor
        # Mocking the run_simulation method
        mock_run_simulation.return_value = \
            SimulationMetrics(total_loss=100, mean_loss=20, median_loss=15, min_loss=5, max_loss=25, std_dev_loss = 3, percentile_95_loss = 2)

        service = AnalysisService(num_companies=2)
        service.companies = self.test_data
        service.run_simulations()

        # Check if the simulator was initialized with the right parameters
        mock_simulator_init.assert_any_call(industry=Industry.FINANCE, revenue=10)
        mock_simulator_init.assert_any_call(industry=Industry.HEALTHCARE, revenue=20)

    @patch('analysis_service.sqlite3.connect')
    def test_get_results_from_db(self, mock_db_connect):
        """
        Test get_results_from_db method.
        """
        service = AnalysisService(num_companies=2)
        service.get_results_from_db()
        mock_db_connect.assert_called()

    @patch('analysis_service.sqlite3.connect')
    def test_get_synthetic_companies_from_db(self, mock_db_connect):
        """
        Test get_synthetic_companies_from_db method.
        """
        service = AnalysisService(num_companies=2)
        service.get_synthetic_companies_from_db()
        mock_db_connect.assert_called()

if __name__ == '__main__':
    unittest.main()
