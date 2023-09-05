from flask import Flask, jsonify, request
import sqlite3
import logging
from cyber_risk_simulator import get_revenue_boundaries_by_band
from simulation_types import parse_revenue_band
from scipy.stats import poisson, norm
from functools import lru_cache
from config_setup import setup_config

# Load configuration data
config_dict = setup_config()

# Initialize the Flask web service
app = Flask(__name__)


@app.route('/', methods=['GET'])
def welcome():
    '''
    Welcome Endpoint
    ---
    This endpoint serves as the root URL of the Monte-Carlo simulation web service.
    It returns a greeting message to indicate that the service is up and running.
    '''
    return 'Hello world from Monte-Carlo simulation web service! :)'



@lru_cache(maxsize=100)
def fetch_cost_by_company_from_db(company_id:int):
    """
    Helper function used to return the average simulation cost for a given company ID from the database.

    This function is optimized using Python's built-in LRU (Least Recently Used) cache with a max size of 100.
    It executes an SQL query to fetch the average 'mean_loss' for a specified company ID from the database.

    Parameters:
        company_id (int): The unique identifier for the company whose simulation cost needs to be fetched.

    """
    logging.debug(f'executing query for {company_id=}')
    with sqlite3.connect(config_dict['db_path']) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT mean_loss FROM {config_dict['simulations_table']} WHERE company_id = ?", (company_id,))
        return cursor.fetchone()
    

@app.route('/get_results_by_id/<company_id>', methods=['GET'])
def get_results_by_id(company_id:int):
    '''
    Fetches and returns the average simulation cost for a given company ID.

    This endpoint serves as an HTTP GET method that receives a company_id as a URL parameter.
    It uses the helper function `fetch_cost_by_company_from_db` to fetch the average simulation cost
    for the specified company ID from the database. 

    URL Endpoint: '/get_results_by_id/<company_id>'

    Parameters:
        company_id (int): The unique identifier for the company whose simulation cost is being retrieved.

    Returns:
        JSON, HTTP Status Code: A JSON object containing the average simulation cost and an HTTP status code.

        - If the company ID exists and the average simulation cost is found, it returns a JSON object
          containing the average simulation cost and a 200 HTTP status code.

        - If the company ID does not exist or no data is available, it returns a JSON object containing an
          "error" message and a 404 HTTP status code.

        - If an exception occurs, it returns a JSON object containing an "error" message and a 500 HTTP
          status code.

    Examples:
        GET /get_results_by_id/12345 -> Returns {'average simulation cost': 10000}, 200
        GET /get_results_by_id/67890 -> Returns {'error': 'no company found'}, 404
    '''

    logging.debug(f'start of get_results_by_id GET method for {company_id=}')
    try:
        result = fetch_cost_by_company_from_db(company_id)
        
        if result:
            logging.info(f'average simulation cost for {company_id=} is: {result[0]}')
            return jsonify({'average simulation cost': result[0]}), 200
        else:
            logging.debug('no company found')
            return jsonify({'error': 'no company found'}), 404
            
    except Exception as e:
        logging.error(f'error: {e}')
        return jsonify({'error': e}), 500


@lru_cache(maxsize=100)
def fetch_cost_by_revenue_and_industry_from_db(revenue_bands_str:tuple, industries_str:tuple)->list:
    '''
    Helper function used to retrieve the average cost for companies filtered by given revenue bands and industries.

    This function is cached using LRU caching to speed up repeated queries with the same parameters.

    Parameters:
    - revenue_bands (tuple): A list of strings representing the revenue bands to filter by.
    - industries (tuple): A list of strings representing the industries to filter by.
    '''

    logging.debug(f"get_results_by_segmentation: {revenue_bands_str=}")
    logging.debug(f"get_results_by_segmentation: {industries_str=}")
    revenue_bands = [parse_revenue_band(band) for band in revenue_bands_str]
    bounds = [(revenue_min, revenue_max) for revenue_min, revenue_max in map(get_revenue_boundaries_by_band, revenue_bands)]

    # Dynamically construct the SQL query
    revenue_clauses, revenue_params, industry_clauses = [], [], [] 
    for lower, upper in bounds:
        revenue_clauses.append("? < revenue_usd AND revenue_usd <= ?")
        revenue_params.extend([lower, upper])

    query_for_companies = f'''SELECT company_id
               FROM {config_dict['synthetic_companies_table']}
               WHERE industry IN ({",".join("?" * len(industries_str))}) AND 
               (revenue_usd < 0 {["","OR (" + " OR ".join(revenue_clauses) + ")"][len(bounds)>0]})'''

    query_for_avg_cost = f"SELECT avg(mean_loss) FROM {config_dict['simulations_table']} WHERE company_id in ({query_for_companies})"

    logging.debug(f"full query for results by segmentation: {query_for_avg_cost}")

    # Execute the query
    with sqlite3.connect(config_dict['db_path']) as conn:
        cursor = conn.cursor()
        cursor.execute(query_for_avg_cost, list(industries_str) + revenue_params)
        result = cursor.fetchone() 
    return result



@app.route('/get_results_by_segmentation', methods=['GET'])
def get_results_by_segmentation():
    '''
    Fetches the average simulation cost for companies based on specified segmentation criteria.

    Query Parameters:
        - revenue (mandatory): A list of revenue bands to filter companies. Multiple bands can be specified.
        - industry (mandatory): A list of industries to filter companies. Multiple industries can be specified.

    Returns:
        JSON object containing the 'average_simulation_cost' if companies are found, 404 error otherwise.

    Example:
        GET /get_results_by_segmentation?revenue=100M,500M&industry=finance,healthcare

        Success Response:
            {
                "average simulation cost": 1234.56
            }

        Error Response:
            404:
            {
                "error": "no companies found"
            }

            500:
            {
                "error": "<Exception message>"
            }
    '''

    try:
        logging.debug(f'start of get_results_by_segmentation GET method')
        revenue_bands = request.args.getlist('revenue')
        industries = request.args.getlist('industry')
        result = fetch_cost_by_revenue_and_industry_from_db(tuple(revenue_bands), tuple(industries))
        
        if result[0]:
            logging.info(f'average simulation cost for companies in the given segmentation is: {result[0]}')
            return jsonify({'average simulation cost': result[0]}), 200
        else:
            logging.error('no companies found')
            return jsonify({'error': 'no companies found'}), 404
            
    except Exception as e:
        logging.error(f'error: {e}')
        return jsonify({'error': e}), 500

# Run the WebService
if __name__ == '__main__':
    app.run(debug=True)
