import logging

def setup_logger():
    """
    Sets up the logger configuration.
    """
    logger = logging.getLogger("fuel_price_tracker")
    logger.setLevel(logging.INFO)
    
    # Create file handler which logs even debug messages
    fh = logging.FileHandler("fuel_price_tracker.log")
    fh.setLevel(logging.INFO)
    
    # Create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Create a formatter and set it for the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    # Add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger

# Set up the logger
logger = setup_logger()
