import unittest
from unittest.mock import patch, Mock
from web_service import app
import json

class TestWebService(unittest.TestCase):
    """
    Unit test class for testing the web service.
    """

    def setUp(self):
        """
        Set up the test client for Flask application.
        """
        app.testing = True
        self.client = app.test_client()

    def test_welcome(self):
        """
        Test the root URL to ensure it returns the welcome message.
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Hello world from Monte-Carlo simulation web service! :)')

    @patch('web_service.fetch_cost_by_company_from_db')
    def test_get_results_by_id(self, mock_fetch_cost):
        """
        Test getting results by company ID with a valid company.
        """
        mock_fetch_cost.return_value = (10000,)

        response = self.client.get('/get_results_by_id/12345')
        json_data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_data['average simulation cost'], 10000)

    @patch('web_service.fetch_cost_by_company_from_db')
    def test_get_results_by_id_no_company(self, mock_fetch_cost):
        """
        Test getting results by company ID when the company does not exist.
        """
        mock_fetch_cost.return_value = None

        response = self.client.get('/get_results_by_id/67890')
        json_data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(json_data['error'], 'no company found')

    @patch('web_service.fetch_cost_by_revenue_and_industry_from_db')
    def test_get_results_by_segmentation(self, mock_fetch_cost_by_segmentation):
        """
        Test getting results by segmentation with valid revenue and industry filters.
        """
        mock_fetch_cost_by_segmentation.return_value = (1234.56,)

        response = self.client.get('/get_results_by_segmentation?revenue=100M,500M&industry=finance,healthcare')
        json_data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_data['average simulation cost'], 1234.56)

    @patch('web_service.fetch_cost_by_revenue_and_industry_from_db')
    def test_get_results_by_segmentation_no_companies(self, mock_fetch_cost_by_segmentation):
        """
        Test getting results by segmentation when no companies match the filters.
        """
        mock_fetch_cost_by_segmentation.return_value = (None,)

        response = self.client.get('/get_results_by_segmentation?revenue=100M,500M&industry=finance,healthcare')
        json_data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(json_data['error'], 'no companies found')

if __name__ == '__main__':
    unittest.main()
