# Monte Carlo Exercise

## Part 1 - Monte Carlo Simulation 
Write a Python program that performs a [Monte Carlo simulation](https://aws.amazon.com/what-is/monte-carlo-simulation/#seo-faq-pairs#how-does-the-monte-carlo-simulation-work) to estimate the cyber risk for a given company based on its industry and revenue. 
Your program should:

* Take as input the number_of_simulations (default_value=10_000), industry, and revenue of the company. 
* Fetch the frequency and cost distributions according to the industry and revenue.  
* Generate number_of_simulations random samples from the frequency and cost distributions - assume a Poisson distribution for frequency and normal distribution for cost with the given values in the attached json [(idustries_revenue_stats.json)](./idustries_revenue_stats.json).
* Calculate the cyber risk for each simulation - the sum of costs of all attacks in a given simulation.

In order to get the `(industry, revenue) -> attack_probability, impact cost distributions` values, utilize a table that maps each `(industry, revenue)` combination to a corresponding distribution from the attached json file. 
- The frequency value can be used as the lambda parameter of the poisson distribution.
- The cost value can be used as the mean of the normal distribution where the std should be 10% of the cost. 

### Program Output

Table format of all simulations results with the following attributes (for each simulation), `simulation_id, attack_id, cost`  
For example (csv format):
  ```
  simulation, attack_id, cost
  1,1,100000
  1,2,300000
  2,3,80000
  5,4,500000
  ```

## Part 2 - analysis service

1. Generate a random dataset of 1000 synthetic companies, each with the following attributes:
* company_id - Unique identifier of the company
* Revenue (USD) - Rounded to the nearest million, from a continuous variable with values ranging from 1 million to 1000 million.
* Industry - Categorical variable with values from a predefined set of industries (e.g., healthcare, finance, retail, etc.)

2. Run your monte carlo program from part 1 on the dataset and store the results on presistent storage.

3. Write a web service with 2 endpoints:
   <br />a. `get_results_by_id(company_id: str) -> float` - returns average_simulation_cost
   <br />b. `get_results_by_segmentation(revenues: List[Revenue], industries: List[Industry]) -> float` - returns the average of average_simulation_cost of the given companies in the sampled dataset.

Please consider response time (latency) and memory usage when developing the service.

## Please pay attention to

* The project should be submitted in a working state
* Code readability, structure, and Python conventions
* Input validation
* Errors should be handled gracefully
* Logging
* The assignment should include a simple readme file with installation instructions
* Feel free to use python libraries and open APIs as you see fit
* In order to submit the exercise, please fork this repository and submit it using Github
* Finally, you should aim to write clean, well-organized code that is easy to read and modify.
							 								
*** Attached is a json file with the industries x revenue stats mapping

## Resources 
[How does a Monte carlo simulation works](https://aws.amazon.com/what-is/monte-carlo-simulation/#seo-faq-pairs#how-does-the-monte-carlo-simulation-work)

