# Monte Carlo simulation for cyber risk

## Monte Carlo simulation 
Monte Carlo simulation to estimate the cyber risk for a given company based on its industry and revenue. 

### requirements

* Take as input the number_of_simulations (default_value=10_000), industry, and revenue of the company. 
* Fetch the frequency and cost distributions according to the industry and revenue.  
* Generate number_of_simulations random samples from the frequency and cost distributions - assume a Poisson distribution for frequency and normal distribution for cost with the given values in the attached json [(idustries_revenue_stats.json)](./idustries_revenue_stats.json).
* Calculate the cyber risk for each simulation - the sum of costs of all attacks in a given simulation.


  
In order to get the `(industry, revenue) -> attack_probability, impact cost distributions` values, utilize a table that maps each `(industry, revenue)` combination to a corresponding distribution from the attached json file. 
- The frequency value can be used as the lambda parameter of the poisson distribution.
- The cost value can be used as the mean of the normal distribution where the std should be 10% of the cost. 

### Output

Table format of all simulations results with the following attributes (for each simulation), `simulation_id, attack_id, cost`  
For example (csv format):
  ```
  simulation, attack_id, cost
  1,1,100000
  1,2,300000
  2,3,80000
  5,4,500000
  ```

## Analysis service

1. Analysis service generating a random dataset of 1000 synthetic companies, each with the following attributes:
* company_id - Unique identifier of the company
* Revenue (USD) - Rounded to the nearest million, from a continuous variable with values ranging from 1 million to 1000 million.
* Industry - Categorical variable with values from a predefined set of industries (e.g., healthcare, finance, retail, etc.)

2. Running monte carlo simulation on the dataset and storing the results on persistent storage.

## Web Service
Web service with 2 endpoints:
<br />a. `get_results_by_id(company_id: str) -> float` - returns average_simulation_cost
<br />b. `get_results_by_segmentation(revenues: List[Revenue], industries: List[Industry]) -> float` - returns the average of average_simulation_cost of the given companies in the sampled dataset.



## Setup
1. Repository contains the following files:<br>
    monte_carlo.log - log file which represents logs of sanity flows executed in monte_carlo.ipynb for all the modules of the exercise<br>
	monte_carlo.db  - sqlite3 DB file with simulation results and companies' synthetic data <br>
	simulation_results_DATE.csv - results of monte-carlo simulation on a specific company <br>
    industries_revenue_stats.json -  industry / revenue stats mapping json<br>
    monte_carlo.ipynb.ipynb -  sanity testing for different modules of the monte-carlo simulation <br>
    config.ini -  configuration file where you can set the following <br>
                  LOG_LEVEL - set log level<br>
                  STATS_PATH  - path to json stats mapping file <br>
                  DB_PATH - sqlite3 DB path<br>
				  SIMULATIONS_TABLE_NAME - table name for the simulation results<br>
				  SYNTHETIC_COMPANIES_TABLE_NAME - table name for the synthetic companies data <br>
    config_setup.py - configuration module that handles loading congigurations from config.ini <br>
	simulation_types.py - relevant types handcrafted  for the  simulation modules <br>
	analysis_service.py - analysis module for monte-carlo simulation <br>
	cyber_risk_simulator.py - simulation module for cyber risk<br>
	web_service.py - web service for getting simulation results from DB <br>
	test_analysis_service.py - unit tests for analysis_service <br>
	test_cyber_risk_simulator.py - unit tests for cyber risk simulator <br>
	test_web_service.py- unit tests for web service<br>


2. Required python libraries<br>
	pandas numpy configparser flask sqlite3 scipy <br><br>

3. How to run the  web service? Simply Execute the following command from the relevant path:<br>
	python web_service.py <br><br>
	Unless configured otherwise  - you can access the web service on local machine on: http://127.0.0.1:5000


4. Unit tests can be executed like any other Python script:
	python test_cyber_risk_simulator.py
	python test_analysis_service.py
	python test_web_service.py

## Resources 
[How does a Monte carlo simulation works](https://aws.amazon.com/what-is/monte-carlo-simulation/#seo-faq-pairs#how-does-the-monte-carlo-simulation-work)