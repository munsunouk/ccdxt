from web3.logs import DISCARD
from web3.datastructures import AttributeDict

import datetime

class Transaction(object) :
    
    def __init__(self,) :
        
        self.transaction_hash = None
        self.status = None
        self.block = None
        self.timestamp = None
        # self.from = None
        self.amountIn = None
        self.to = None
        self.amountOut = None
        self.transaction_fee = None
        
    def fetch_transaction(self, tx, round = None):
        
        '''
        Takes built transcations and transmits it to ethereum
        
        Parameters
        ----------
        w3 : web3 object
        privateKey : users private key
        tx : Transaction to be transmitted
        
        Returns
        -------
        Transaction reciept = 
        
            AttributeDict(
                {
                    'blockHash': HexBytes('0x01af4f5a6e68726ab17426e1b1f43f8b2e2602676626d936c4e5dfe045d91957'), 
                    'blockNumber': 99072001, 
                    'contractAddress': None, 
                    'cumulativeGasUsed': 88596, 
                    'effectiveGasPrice': 250000000000, 
                    'from': '0xdaf07D203C01467644e7305BE9caA6E9Fe12ac9a', 
                    'gasUsed': 31259, 
                    'logs': [AttributeDict(
                        {
                            'address': '0xceE8FAF64bB97a73bb51E115Aa89C17FfA8dD167', 
                            'blockHash': HexBytes('0x01af4f5a6e68726ab17426e1b1f43f8b2e2602676626d936c4e5dfe045d91957'), 
                            'blockNumber': 99072001, 
                            'data': '0x000000000000000000000000000000000000000000000000000000003b9aca00', 
                            'logIndex': 1, 
                            'removed': False, 
                            'topics': [HexBytes('0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925'), 
                            HexBytes('0x000000000000000000000000daf07d203c01467644e7305be9caa6e9fe12ac9a'), 
                            HexBytes('0x000000000000000000000000c6a2ad8cc6e4a7e08fc37cc5954be07d499e7654')], 
                            'transactionHash': HexBytes('0x02bf327810bc2113eecf5d91f110ad2b91310272576b5ee5353a69e33e98c030'), 
                            'transactionIndex': 1
                        }
                    )],
                    'logsBloom': HexBytes('0x00000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000001000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000010000040000000000000000000006000000000000000000000000000000000'), 
                    'status': 1, 
                    'to': '0xceE8FAF64bB97a73bb51E115Aa89C17FfA8dD167', 
                    'transactionHash': HexBytes('0x02bf327810bc2113eecf5d91f110ad2b91310272576b5ee5353a69e33e98c030'), 
                    'transactionIndex': 1, 
                    'type': '0x2'
                }
            )
        '''
        signed_tx =self.w3.eth.account.signTransaction(tx, self.privateKey)
        
        tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)

        tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)

        if tx_receipt["status"] != 1:

            return self.fetch_trade_fail(tx_hash)
        
        if round == 'CHECK' :
            
            return print("approved token :",tx_receipt)
        
        if round == 'BRIDGE' :
            
            function, input_args = self.routerContract.decode_function_input(self.get_transaction_data_field(tx))
            
            deposit = self.routerContract.events.Deposit()
            
            events = deposit.processReceipt(tx_receipt, errors=DISCARD)
            
            amount_in = events[-1]["args"]['amount']
            
            txDict = {
                
                'transaction_hash' : tx_receipt['transactionHash'].hex(),
                'status' : tx_receipt["status"],
                'block' :  tx_receipt['blockNumber'],
                'timestamp' : datetime.datetime.now(),
                'function' : function,
                'from' : tx_receipt['from'],
                'amountIn' : amount_in,
                'tokenA' : self.tokenSymbol,
                'to' : tx_receipt['to'],
                'from_chain' : self.fromChain,
                'to_chain' : self.toChain,
                'transaction_fee:' : tx_receipt['gasUsed'] * tx_receipt['effectiveGasPrice'] / 10 ** 18 ,
                
            }
            
            return txDict
        
        if round == 'SWAP' :

            function, input_args = self.routerContract.decode_function_input(self.get_transaction_data_field(tx))
            path = input_args["path"]
            
            swap = self.routerContract.events.ExchangePos()
            
            events = swap.processReceipt(tx_receipt, errors=DISCARD)
            
            amount0_in = events[-1]["args"]["amountA"]
            amount1_out = events[-1]["args"]["amountB"]
            
            amount0_in = self.to_value(amount0_in, self.decimals(self.tokenAsymbol))
            amount1_out = self.to_value(amount1_out, self.decimals(self.tokenBsymbol))

            txDict = {
                
                'transaction_hash' : tx_receipt['transactionHash'].hex(),
                'status' : tx_receipt["status"],
                'block' :  tx_receipt['blockNumber'],
                'timestamp' : datetime.datetime.now(),
                'function' : function,
                'from' : tx_receipt['from'],
                'amountIn' : amount0_in,
                'tokenA' : self.tokenAsymbol,
                'to' : tx_receipt['to'],
                'amountOut' : amount1_out,
                'tokenB' : self.tokenBsymbol,
                'transaction_fee:' : tx_receipt['gasUsed'] * tx_receipt['effectiveGasPrice'] / 10 ** 18 ,
                
            }
            
            return txDict
        
    def fetch_trade_fail(self,tx_hash) :

        tx = self.w3.eth.get_transaction(tx_hash)
    
        replay_tx = {
            "to": tx["to"],
            "from": tx["from"],
            "value": tx["value"],
            "data": self.get_transaction_data_field(tx),
        }

        # Replay the transaction locally
        try:
            result = self.w3.eth.call(replay_tx)
        except ValueError as e:
            self.logger.debug("Revert exception result is: %s", e)
            assert len(e.args) == 1, f"Something fishy going on with {e}"

            data = e.args[0]
            if type(data) == str:
                # BNB Smart chain + geth
                return data
            else:
                # Ganache
                # {'message': 'VM Exception while processing transaction: revert BEP20: transfer amount exceeds balance', 'stack': 'CallError: VM Exception while processing transaction: revert BEP20: transfer amount exceeds balance\n    at Blockchain.simulateTransaction (/usr/local/lib/node_modules/ganache/dist/node/1.js:2:49094)\n    at processTicksAndRejections (node:internal/process/task_queues:96:5)', 'code': -32000, 'name': 'CallError', 'data': '0x08c379a00000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000002642455032303a207472616e7366657220616d6f756e7420657863656564732062616c616e63650000000000000000000000000000000000000000000000000000'}
                return data["message"]
        except Exception as e:
            # Ethereum Tester
            return e.args[0]

        # TODO:
        # Not sure why this happens.
        # When checking on bscchain:
        # This transaction has been included and will be reflected in a short while.

        receipt = self.w3.eth.get_transaction_receipt(tx_hash)
        if receipt.status != 0:
            self.logger.error("Queried revert reason for a transaction, but receipt tells it did not fail. tx_hash:%s, receipt: %s", tx_hash.hex(), receipt)

        current_block_number = self.w3.eth.block_number
        # TODO: Convert to logger record
        self.logger.error(f"Transaction succeeded, when we tried to fetch its revert reason. Hash: {tx_hash.hex()}, tx block num: {tx.blockNumber}, current block number: {current_block_number}, transaction result {result.hex()}. Maybe the chain tip is unstable?")
        return "<could not extract the revert reason>"
    
    def get_transaction_data_field(self,tx: AttributeDict) -> str:

        """Get the "Data" payload of a transaction.
        Ethereum Tester has this in tx.data while Ganache has this in tx.input.
        Yes, it is madness.
        Example:
        .. code-block::
            tx = web3.eth.get_transaction(tx_hash)
            function, input_args = router.decode_function_input(get_transaction_data_field(tx))
            print("Transaction {tx_hash} called function {function}")
        """
        if "data" in tx:
            return tx["data"]
        else:
            return tx["input"]