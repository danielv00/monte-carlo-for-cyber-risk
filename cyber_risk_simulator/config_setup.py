import configparser
import logging

def setup_config():
    '''
    Setup and return the configuration settings from a 'config.ini' file.
    
    This function reads a configuration INI file to setup logging and database settings,
    and returns a dictionary containing these configuration values for further use.

    Returns:
    --------
    config_dict : dict
        A dictionary containing the following key-value pairs:
        
        - 'log_level': The log level to be used for logging. E.g., 'DEBUG', 'INFO', etc.
        - 'db_path': The path to the SQLite database.
        - 'simulations_table': The name of the table containing simulation data.
        - 'synthetic_companies_table': The name of the table containing synthetic companies' data.
        - 'stats_csv': The path to the CSV file containing statistics.

    Usage Example:
    --------------
    config = setup_config()
    log_level = config['log_level']
    db_path = config['db_path']

    '''
    config_dict = {}
    
    # Set config file
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    # Set up logging
    log_level = config.get('LOG', 'LOG_LEVEL')
    logging.basicConfig(filename='monte_carlo.log', level=log_level)
    config_dict['log_level'] = log_level

    # Set up DB data
    config_dict['db_path'] = config.get('DATABASE', 'DB_PATH')
    config_dict['simulations_table'] = config.get('DATABASE', 'SIMULATIONS_TABLE_NAME')
    config_dict['synthetic_companies_table'] = config.get('DATABASE', 'SYNTHETIC_COMPANIES_TABLE_NAME')
    
    # Set up csv data
    config_dict['stats_csv'] = config.get('CSV', 'STATS_PATH')
    
    return config_dict

