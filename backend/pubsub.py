import os
import time
import requests

from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
from pubnub.callbacks import SubscribeCallback

from backend.blockchain.block import Block
from backend.blockchain.blockchain import Blockchain
from backend.wallet.transaction import Transaction

from backend.app.logging import logger

pnconfig = PNConfiguration()
pnconfig.publish_key = os.environ.get("PUBNUB_PUBLISH_KEY")
pnconfig.subscribe_key = os.environ.get("PUBNUB_SUBSCRIBE_KEY")
pnconfig.user_id = os.environ.get("PUBNUB_USER_ID", "blockchain-node-default")

CHANNELS = {"TEST": "TEST", "BLOCK": "BLOCK", "TRANSACTION": "TRANSACTION"}


class Listener(SubscribeCallback):
    def __init__(self, blockchain, transaction_pool):
        self.blockchain = blockchain
        self.transaction_pool = transaction_pool

    def message(self, pubnub, message_object):
        print(
            f"-- Channel: {message_object.channel} | Message: {message_object.message}"
        )

        if message_object.channel == CHANNELS["BLOCK"]:
            block = Block.from_json(message_object.message)
            potential_chain = self.blockchain.chain[:]
            potential_chain.append(block)

            try:
                self.blockchain.replace_chain(potential_chain)

                self.transaction_pool.clear_blockchain_transactions(self.blockchain)

                print("-- Successfully replaced the local chain")
            except Exception as e:
                # print(f'\n -- Did not replace chain: {e}')

                # If we can't validate the block, try to sync the full blockchain
                # This handles cases where we're missing previous blocks
                self.sync_blockchain()

        elif message_object.channel == CHANNELS["TRANSACTION"]:
            transaction = Transaction.from_json(message_object.message)
            self.transaction_pool.set_transaction(transaction)
            print("-- Set the new transaction in the transaction pool")

    def sync_blockchain(self):
        """
        Synchronize the local blockchain with the root node.
        This is called when we receive a block we can't validate.
        """
        try:
            # Get the root backend host (main node)
            root_host = os.environ.get("ROOT_HOST", "localhost")
            root_port = os.environ.get("ROOT_PORT", "5050")

            print(f"-- Attempting to sync blockchain from {root_host}:{root_port}")

            # Request the full blockchain from the root node
            response = requests.get(f"http://{root_host}:{root_port}/api/blockchain")
            result_blockchain = Blockchain.from_json(response.json())

            # Replace our local chain with the synchronized chain
            self.blockchain.replace_chain(result_blockchain.chain)

            print(
                f"-- Successfully synchronized! Chain length: {len(self.blockchain.chain)}"
            )
        except Exception as e:
            print(f"-- Could not synchronize blockchain: {e}")


class PubSub:
    """
    Handles the publish/subscribe layer of the application.
    Provides communication between blockchain nodes.
    """

    def __init__(self, blockchain, transaction_pool):
        self.blockchain = blockchain
        self.transaction_pool = transaction_pool
        self.pubnub = None

    def start(self):
        """Initialize PubNub and start subscriptions."""
        pnconfig = PNConfiguration()
        pnconfig.publish_key = os.environ.get("PUBNUB_PUBLISH_KEY")
        pnconfig.subscribe_key = os.environ.get("PUBNUB_SUBSCRIBE_KEY")
        pnconfig.user_id = os.environ.get("PUBNUB_USER_ID", "blockchain-node-main")

        self.pubnub = PubNub(pnconfig)
        self.pubnub.subscribe().channels(CHANNELS.values()).execute()
        self.pubnub.add_listener(Listener(self.blockchain, self.transaction_pool))
        logger.info("-- PubNub started")

    def stop(self):
        """Stop PubNub cleanly."""
        if self.pubnub:
            self.pubnub.unsubscribe_all()
            self.pubnub.stop()
            print("-- PubNub stopped")
            self.pubnub = None

    def publish(self, channel, message):
        try:
            result = self.pubnub.publish().channel(channel).message(message).sync()
            print(f"-- Published to {channel}: {result.status.is_error()}")
        except Exception as e:
            print(f"-- Error publishing to {channel}: {e}")

    def broadcast_block(self, block):
        self.publish(CHANNELS["BLOCK"], block.to_json())

    def broadcast_transaction(self, transaction):
        self.publish(CHANNELS["TRANSACTION"], transaction.to_json())


def main():
    pubsub = PubSub()

    time.sleep(1)

    pubsub.publish(CHANNELS["TEST"], {"foo": "bar"})


if __name__ == "__main__":
    main()
