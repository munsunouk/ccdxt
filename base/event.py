from web3.contract import Contract
from web3.logs import DISCARD, IGNORE
from web3.datastructures import AttributeDict
from web3._utils.events import EventLogErrorFlags

import logging

swapDict = {
    "KLAYTN": {
        "Klayswap": {
            "event": [-1, "ExchangePos"],
            "amount0_in": ["amountA"],
            "amount1_out": ["amountB"],
        },
    },
    "MATIC": {
        "Meshswap": {
            "event": [-1, "ExchangePos"],
            "amount0_in": ["amount0"],
            "amount1_out": ["amount1"],
        },
    },
    "MOOI": {
        "Mooiswap": {
            "event": [-1, "Swap"],
            "amount0_in": ["amount0In", "amount1In"],
            "amount1_out": ["amount0Out", "amount1Out"],
        }
    },
}

bridgeDict = {
    "Orbitbridge": {
        "Vault": {"event": [-1, "Deposit"], "amount0_in": ["amount"]},
        "Minter": {"event": [-1, "SwapRequest"], "amount0_in": ["amount"]},
    },
}

transferDict = {
    "Orbitbridge": {
        "event": [0, "Transfer"],
        "amount0_in": ["value"],
    },
}

add_liquidityDict = {
    "Traderjoe": {
        "event": [0, "Transfer"],
        "amount0_in": ["value"],
    },
}

txDict = {
    "transaction_hash": None,
    "status": None,
    "block": None,
    "timestamp": None,
    "function": None,
    "from": None,
    "amountIn": None,
    "tokenA": None,
    "to": None,
    "amountOut": None,
    "tokenB": None,
    "transaction_fee:": None,
}


class Event:
    def __init__(self, swapDict, bridgeDict, txDict):
        """
        Initialize the Event class with the swap, bridge, and tx dictionaries.

        Parameters:
        ----------------
        - swapDict (dict): dictionary of swap events
        - bridgeDict (dict): dictionary of bridge events
        - txDict (dict): dictionary of tx events
        """

        self.swapDict = swapDict
        self.bridgeDict = bridgeDict
        self.txDict = txDict

    # @classmethod
    async def swap(
        chainsName: str,
        marketName: str,
        tx_receipt: AttributeDict,
        routerContract: Contract,
    ):
        """
        Extract swap event data from a transaction receipt.

        Parameters:
        --------------
        - chainsName (str): name of the chain
        - marketName (str): name of the market
        - tx_receipt (AttributeDict): transaction receipt
        - routerContract (Contract): contract instance

        Returns:
        --------------
        - tuple: tuple containing the amount of token A in and token B out

        """

        if chainsName not in swapDict:

            events_param_list = [0, "Transfer"]
            amount_in_params = ["value"]
            amount_out_params = ["value"]

        else:

            if marketName not in swapDict[chainsName]:

                events_param_list = [0, "Transfer"]
                amount_in_params = ["value"]
                amount_out_params = ["value"]

            else:

                events_param_list = swapDict[chainsName][marketName]["event"]
                amount_in_params = swapDict[chainsName][marketName]["amount0_in"]
                amount_out_params = swapDict[chainsName][marketName]["amount1_out"]

        swap = routerContract.events[events_param_list[1]]()

        events = swap.process_receipt(tx_receipt, errors=DISCARD)

        amount0_in = max(
            [events[events_param_list[0]]["args"][param] for param in amount_in_params]
        )

        amount1_out = max([events[-1]["args"][param] for param in amount_out_params])

        return amount0_in, amount1_out

    # @classmethod
    async def bridge(
        bridgeName: str, tx_receipt: AttributeDict, routerContract: Contract, *args, **kwargs
    ):
        """
        Extract bridge event data from a transaction receipt.

        Parameters:
        - bridgeName (str): name of the bridge
        - versionName (str): name of the version
        - tx_receipt (AttributeDict): transaction receipt
        - routerContract (Contract): contract instance

        Returns:
        - int: amount of token in

        """

        if kwargs["version"]:

            bridge = routerContract.events[bridgeDict[bridgeName][kwargs["version"]]["event"][1]]()
            events = bridge.process_receipt(tx_receipt, errors=DISCARD)
            amount_in_params = bridgeDict[bridgeName][kwargs["version"]]["amount0_in"]

            amount0_in = max(
                [
                    events[bridgeDict[bridgeName][kwargs["version"]]["event"][0]]["args"][param]
                    for param in amount_in_params
                ]
            )

        else:

            bridge = routerContract.events[bridgeDict[bridgeName]["event"][1]]()
            events = bridge.process_receipt(tx_receipt, errors=DISCARD)
            amount_in_params = bridgeDict[bridgeName]["amount0_in"]
            amount0_in = max(
                [
                    events[bridgeDict[bridgeName]["event"][0]]["args"][param]
                    for param in amount_in_params
                ]
            )

        return amount0_in

    async def transfer(
        bridgeName: str,
        tx_receipt: AttributeDict,
        routerContract: Contract,
    ):
        """
        Extract bridge event data from a transaction receipt.

        Parameters:
        - bridgeName (str): name of the bridge
        - versionName (str): name of the version
        - tx_receipt (AttributeDict): transaction receipt
        - routerContract (Contract): contract instance

        Returns:
        - int: amount of token in

        """

        bridge = routerContract.events[transferDict[bridgeName]["event"][1]]()

        events = bridge.process_receipt(tx_receipt, errors=DISCARD)

        amount_in_params = transferDict[bridgeName]["amount0_in"]

        amount0_in = max(
            [
                events[transferDict[bridgeName]["event"][0]]["args"][param]
                for param in amount_in_params
            ]
        )

        return amount0_in
