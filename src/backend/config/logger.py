import logging

def setup_logger():
    # Set up logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    # Add a debug file handler
    debug_handler = logging.FileHandler('debug.log')
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s'))
    logging.getLogger().addHandler(debug_handler)
