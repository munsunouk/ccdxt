import json
from pathlib import Path
import os
from web3._utils.abi import get_abi_output_types
from ccdxt.base.exchange import Exchange

class Multicall(Exchange):
    
    def __init__(self, chainName):
        super().__init__()
        
        self.maxRetries = 4
        self.batches = 1
        self.verbose = False
        self.chainName = chainName
        
        self.mcContract = self.set_multicall(chainName)
    
    def set_multicall(self,chainName) :
        
        # swapscanner = "0xf50782a24afcb26acb85d086cf892bfffb5731b5"
        test = "0x778fabd0de783287853372c83dfcaba83bdf5f9c"
        
        basePath = Path(__file__).resolve().parent.parent
        
        multicall_path = os.path.join(basePath , "contract", "abi", 'multiCall.json')
        
        if Path(multicall_path).exists() :
            with open(multicall_path, "rt", encoding="utf-8") as f:
                mulAbi = json.load(f)
                
        self.load_multicall(chainName)
        
        self.reset()
        
        multiCall = self.w3.eth.contract(self.set_checksum(swapscanner), abi=mulAbi)
        return multiCall
    
    def addCall(self, address, functionName, args=None):
        if not args is None:
            args = self.listToString(args)
            
        address = self.set_checksum(address)
        contract = self.get_contract(address, self.chains['chainAbi'])
        callData = self.getCallData(contract, functionName, args)
        fn = self.getFunction(contract, functionName)
        self.payload.append((address, callData))
        self.decoders.append(get_abi_output_types(fn.abi))
        
    def execute(self):
        retries = 0
        outputData = None
        while retries < self.maxRetries:
            retries += 1
            if self.verbose:
                print("Attempt", retries, "of", self.maxRetries)
                print("Executing with", self.batches, "batches!")
            sublistsPayload = self.split(self.payload, self.batches)
            sublistsDecoder = self.split(self.decoders, self.batches)

            try:
                outputData = []
                for sublistPayload, sublistDecoder in zip(sublistsPayload, sublistsDecoder):

                    success = False
                    internalRetries = 0
                    maxInternalRetries = 3
                    while not success and internalRetries < maxInternalRetries:
                        try:
                            output = self.mcContract.functions.aggregate(sublistPayload).call()
                            outputDataRaw = output[1]
                            for rawOutput, decoder in zip(outputDataRaw, sublistDecoder):
                                outputData.append(self.decodeData(self.listToString(decoder), rawOutput))
                            success = True
                        except OverflowError:
                            internalRetries += 1
                            print("Internal retry", internalRetries, "of", maxInternalRetries)
                        except Exception as e:
                            print("One or more of the calls failed. Please try again after removing the failing call(s).")
                            self.reset()
                            raise e
                    if internalRetries >= maxInternalRetries:
                        raise OverflowError

                break
            except OverflowError:
                self.batches += 1
                print("Too many requests in one batch. Reattempting with", self.batches, "batches...")
            except Exception as e:
                print("Attempt", retries, "of", self.maxRetries, "failed. Retrying...")
				# self.reset()
				# raise e
        self.reset()
        return outputData
    
    def getCallData(self, contract, functionName, argsString):
        args = self.stringToList(argsString)
        callData = contract.encodeABI(fn_name=functionName, args=args)
        return callData
    
    def getFunction(self, contract, functionName):
        fn = contract.get_function_by_name(fn_name=functionName)
        return fn
    
    def stringToList(self, inputString):
        if inputString is None :
            return None
        outputList = json.loads(inputString)
        return outputList
    
    def listToString(self, inputList):
        inputList = self.iterArgs(inputList)
        outputString = json.dumps(inputList)
        return outputString
    
    def split(self, a, n):
        k, m = divmod(len(a), n)
        return list(a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))
    
    def reset(self):
        self.payload = []
        self.decoders = []