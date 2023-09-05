import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
from cyber_risk_simulator import CyberRiskSimulator 
from simulation_types import Industry, RevenueBand, SimulationMetrics
import logging
from config_setup import setup_config

# Load configuration data
config_dict = setup_config()

class AnalysisService:
    """
    This class is responsible for running simulations on synthetic companies,
    saving the simulation results and synthetic companies to a database,
    and retrieving these results when needed.
    """
    def __init__(self, num_companies: int = 1000):
        """
        Initialize the AnalysisService object.
        
        Parameters:
            num_companies (int, optional): The number of synthetic companies to generate.
                                           Default is 1000.
        """
        logging.info("Initializing AnalysisService.")
        self.num_companies = num_companies
        self.companies = self._generate_synthetic_companies()

    def _generate_synthetic_companies(self) -> pd.DataFrame:
        """
        Generate synthetic company data including company_id, revenue, and industry.
        
        Returns:
            pd.DataFrame: DataFrame containing synthetic company data.
        """
        logging.debug("Generating synthetic companies.")
        # Generating company_id
        company_ids = [company_id + 1 for company_id in range(self.num_companies)]

        # Generating Revenue
        revenues = np.random.uniform(1, 1000, self.num_companies)
        revenues = np.round(revenues)

        # Generating Industry
        industries = [e.name.lower() for e in Industry]  # Using enum for industries
        industry_data = np.random.choice(industries, self.num_companies)
        
        # Creating DataFrame
        synthetic_companies_df = pd.DataFrame({
            'company_id': company_ids,
            'revenue_usd': revenues,
            'industry': industry_data
        })
        
        self._save_synthetic_companies_to_db(synthetic_companies_df)
        
        return synthetic_companies_df
        
    def _save_synthetic_companies_to_db(self, df: pd.DataFrame):
        """
        Save the generated synthetic companies to a SQLite database.
        
        Parameters:
            df (pd.DataFrame): DataFrame containing synthetic company data.
        """
        logging.debug("Saving synthetic companies to database.")
        with sqlite3.connect(config_dict['db_path']) as conn:
            df.to_sql(config_dict['synthetic_companies_table'], conn, if_exists='replace', index=False)
    
    def _save_simulation_to_db(self, df: pd.DataFrame):
        """
        Save the simulation results to a SQLite database.
        
        Parameters:
            df (pd.DataFrame): DataFrame containing simulation results.
        """
        logging.debug("Saving simulation results to database.")
        with sqlite3.connect(config_dict['db_path']) as conn:
            df.to_sql(config_dict['simulations_table'], conn, if_exists='append', index=False)

    def run_simulations(self):
        """
        Run cyber risk simulations for the synthetic companies and save the results.
        """
        logging.debug("Running simulations.")
        simulation_results = []

        for _, company in self.companies.iterrows():
            industry = Industry.from_string(company['industry'])
            simulator = CyberRiskSimulator(industry=industry, revenue=company['revenue_usd'])
            metrics = simulator.run_simulation()

            # Adding timestamp to each simulation
            timestamp = datetime.now()

            # Storing the results
            simulation_results.append({
                'company_id': company['company_id'],
                'total_loss': metrics.total_loss,
                'mean_loss': metrics.mean_loss,
                'timestamp': timestamp
            })

        # Convert the list of dictionaries to a DataFrame
        results_df = pd.DataFrame(simulation_results)

        # Save results to DB
        self._save_simulation_to_db(results_df)

    def get_results_from_db(self)->pd.DataFrame:
        """
        Retrieve simulation results from the SQLite database.
        
        Returns:
            pd.DataFrame: DataFrame containing the simulation results.
        """
        
        logging.debug("Retrieving simulation results from database.")
        # Connect to SQLite database
        with sqlite3.connect(config_dict['db_path']) as conn:
            # Query the table and load into a DataFrame
            return pd.read_sql(f"SELECT * FROM {config_dict['simulations_table']}", conn)

    def get_synthetic_companies_from_db(self) -> pd.DataFrame:
        """
        Retrieve synthetic companies from the SQLite database.
        
        Returns:
            pd.DataFrame: DataFrame containing synthetic company data.
        """
        
        logging.debug("Retrieving synthetic companies from database.")
        # Connect to SQLite database
        with sqlite3.connect(config_dict['db_path']) as conn:
            # Query the table and load into a DataFrame
            return pd.read_sql(f"SELECT * FROM {config_dict['synthetic_companies_table']}", conn)
