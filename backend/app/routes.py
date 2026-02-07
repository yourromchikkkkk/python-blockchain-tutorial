"""
Flask routes module.
Defines all HTTP endpoints for the blockchain API.
"""

import json
from flask import Flask, jsonify, request, Response

from backend.app.logging import logger
from backend.app.context import app_context
from backend.wallet.transaction import Transaction


def json_response(data, status=200):
    """
    Create a JSON response that preserves large integers.
    Flask's default jsonify converts large ints to floats, which breaks
    cryptographic signatures. This function ensures integers are preserved.
    """
    return Response(
        json.dumps(data, separators=(",", ":")),
        status=status,
        mimetype="application/json",
    )


def register_routes(app: Flask, prefix="/api"):
    """
    Register all routes with the Flask application.

    Args:
        app: Flask application instance
    """
    # Get references to application context objects for convenience
    blockchain = app_context.blockchain
    wallet = app_context.wallet
    transaction_pool = app_context.transaction_pool
    pubsub = app_context.pubsub

    @app.route(f"{prefix}/")
    def route_default():
        return "Welcome to the blockchain"

    @app.route(f"{prefix}/blockchain")
    def route_blockchain():
        return json_response(blockchain.to_json())

    @app.route(f"{prefix}/blockchain/range")
    def route_blockchain_range():
        # http://localhost:5050/blockchain/range?start=2&end=5
        start = int(request.args.get("start"))
        end = int(request.args.get("end"))

        return jsonify(blockchain.to_json()[::-1][start:end])

    @app.route(f"{prefix}/blockchain/length")
    def route_blockchain_length():
        return jsonify(len(blockchain.chain))

    @app.route(f"{prefix}/blockchain/mine")
    def route_blockchain_mine():
        transaction_data = transaction_pool.transaction_data()
        transaction_data.append(Transaction.reward_transaction(wallet).to_json())
        blockchain.add_block(transaction_data)
        block = blockchain.chain[-1]
        pubsub.broadcast_block(block)
        transaction_pool.clear_blockchain_transactions(blockchain)

        return json_response(block.to_json())

    @app.route(f"{prefix}/wallet/transact", methods=["POST"])
    def route_wallet_transact():
        transaction_data = request.get_json()
        transaction = transaction_pool.existing_transaction(wallet.address)

        if transaction:
            transaction.update(
                wallet, transaction_data["recipient"], transaction_data["amount"]
            )
        else:
            transaction = Transaction(
                wallet, transaction_data["recipient"], transaction_data["amount"]
            )

        pubsub.broadcast_transaction(transaction)
        transaction_pool.set_transaction(transaction)

        return jsonify(transaction.to_json())

    @app.route(f"{prefix}/wallet/info")
    def route_wallet_info():
        return jsonify({"address": wallet.address, "balance": wallet.balance})

    @app.route(f"{prefix}/known-addresses")
    def route_known_addresses():
        known_addresses = set()

        for block in blockchain.chain:
            for transaction in block.data:
                known_addresses.update(transaction["output"].keys())

        return jsonify(list(known_addresses))

    @app.route(f"{prefix}/transactions")
    def route_transactions():
        return jsonify(transaction_pool.transaction_data())
