"""
Application entry point.
Initializes and runs the Flask application with graceful shutdown handling.
"""
import sys
import signal
import time

from backend.app.logging import logger
from backend.app.factory import create_app
from backend.app.context import app_context
from backend.app.polling import start_polling_thread, shutdown_event
from backend.config import AppConfig


# Start the polling thread if configured
polling_thread = start_polling_thread(app_context.blockchain)

# Create the Flask application
app = create_app()


# ------------------------------
# Graceful shutdown
# ------------------------------
def shutdown(signum, frame):
    """
    Handle shutdown signals (SIGTERM, SIGINT) gracefully.
    Stops PubSub, polling thread, and cleans up resources.
    """
    logger.info("Received shutdown signal — exiting...")

    # Stop PubSub
    if app_context.pubsub:
        logger.info("Stopping PubSub")
        app_context.pubsub.stop()

    # Stop polling thread
    shutdown_event.set()
    if polling_thread and polling_thread.is_alive():
        logger.info("Waiting for polling thread to finish...")
        polling_thread.join(timeout=5)

    time.sleep(0.5)
    logger.info("Cleanup complete. Exiting.")
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

# ------------------------------
# Run the Flask app
# ------------------------------
if __name__ == "__main__":
    port = AppConfig.get_port()
    logger.info(f"Starting blockchain node on port {port}")

    app.run(host="0.0.0.0", port=port)
