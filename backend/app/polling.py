"""
Polling thread module for synchronizing blockchain from root node.
"""
import os
import threading
import time
import requests
from backend.app.logging import logger
from backend.blockchain.blockchain import Blockchain
from backend.blockchain.exceptions import ChainLengthException

# Shutdown event for graceful thread termination
shutdown_event = threading.Event()

def poll_root_blockchain(blockchain, root_host, root_port, poll_interval):
    """
    Continuously poll the root blockchain node for updates.
    
    Args:
        blockchain: The local blockchain instance to update
        root_host: Hostname of the root node
        root_port: Port of the root node
        poll_interval: Seconds between polling attempts
    """
    logger.info(
        f"-- Starting polling thread for {root_host}:{root_port} every {poll_interval}s"
    )

    while not shutdown_event.is_set():
        try:
            logger.info(f"-- Polling root blockchain from root_host:root_port {root_host}:{root_port}")
            result = requests.get(f"http://{root_host}:{root_port}/api/blockchain")
            result_blockchain = Blockchain.from_json(result.json())
            blockchain.replace_chain(result_blockchain.chain)
            logger.info(f"-- Successfully polled and updated blockchain from {root_host}")
        except ChainLengthException:
            logger.info("\n -- Local chain is already up to date")
        except Exception as e:
            logger.info(f"\n -- Error polling root blockchain: {e}")

        # Sleep in 1-second increments to allow quick shutdown
        # The allows the thread to check for the shutdown event every second
        for _ in range(poll_interval):
            if shutdown_event.is_set():
                logger.info("--Shutdown_event detected")
                break
            time.sleep(1)


def start_polling_thread(blockchain):
    """
    Start the polling thread if POLL_ROOT environment variable is True.
    
    Args:
        blockchain: The blockchain instance to keep synchronized
        
    Returns:
        The polling thread object, or None if polling is not enabled
    """
    if os.environ.get("POLL_ROOT") != "True":
        return None
    
    poll_interval = int(os.environ.get("POLL_INTERVAL", "15"))
    root_host = os.environ.get("ROOT_HOST", "localhost")
    root_port = int(os.environ.get("ROOT_PORT", "5050"))
    
    # Start polling in a background daemon thread
    polling_thread = threading.Thread(
        target=poll_root_blockchain,
        args=(blockchain, root_host, root_port, poll_interval),
        daemon=False
    )
    polling_thread.start()
    
    return polling_thread

