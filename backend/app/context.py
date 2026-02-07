"""
Application context module.
Manages the core application state including blockchain, wallet, transaction pool, and pubsub.
"""
import random
import requests
from backend.app.logging import logger
from backend.blockchain.blockchain import Blockchain
from backend.blockchain.exceptions import ChainLengthException
from backend.wallet.wallet import Wallet
from backend.wallet.transaction import Transaction
from backend.wallet.transaction_pool import TransactionPool
from backend.pubsub import PubSub
from backend.config import AppConfig


class AppContext:
    """
    Encapsulates all application state and provides initialization logic.
    """
    
    def __init__(self):
        self.blockchain = Blockchain()
        self.wallet = Wallet(self.blockchain)
        self.transaction_pool = TransactionPool()
        self.pubsub = PubSub(self.blockchain, self.transaction_pool)
        
        self.initialize()
    
    def initialize(self):
        """
        Initialize application state based on environment configuration.
        """
        if AppConfig.IS_PEER:
            self.sync_with_root()
        
        if AppConfig.SEED_DATA:
            self.seed_data()
    
    def sync_with_root(self):
        """
        Synchronize blockchain with the root node on startup.
        """
        try:
            result = requests.get(
                f"http://{AppConfig.ROOT_HOST}:{AppConfig.ROOT_PORT}/api/blockchain"
            )
            result_blockchain = Blockchain.from_json(result.json())
            self.blockchain.replace_chain(result_blockchain.chain)
            logger.info("\n -- Successfully synchronized the local chain")
        except ChainLengthException:
            logger.info("\n -- Local chain is already up to date")
        except Exception as e:
            logger.info(f"\n -- Error synchronizing: {e}")
    
    def seed_data(self):
        """
        Seed the blockchain and transaction pool with test data.
        """
        for i in range(10):
            self.blockchain.add_block(
                [
                    Transaction(
                        Wallet(), Wallet().address, random.randint(2, 50)
                    ).to_json(),
                    Transaction(
                        Wallet(), Wallet().address, random.randint(2, 50)
                    ).to_json(),
                ]
            )
        
        for i in range(3):
            transaction = Transaction(Wallet(), Wallet().address, random.randint(2, 50))
            self.pubsub.broadcast_transaction(transaction)
            self.transaction_pool.set_transaction(transaction)


app_context = AppContext()

