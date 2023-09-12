"use strict";
var _a, _b;
Object.defineProperty(exports, "__esModule", { value: true });
exports.configuration = void 0;
var rubic_sdk_1 = require("rubic-sdk");

async function bridge_js(amountA, tokenA, tokenB, fromChain, toChain, account, privateKey, node_url){

    exports.configuration = {
        rpcProviders: {
            network_name: {
                rpcList: [node_url]
            },
        },
    };

    var walletProvider = (_b = {},
    _b[rubic_sdk_1.CHAIN_TYPE.EVM] = {
        address: account,
        core: window.ethereum
    },
    _b);

    // create SDK instance
    const sdk = await RubicSDK.SDK.createSDK(configuration);
    sdk.updateWalletProvider(walletProvider);
    
    // calculate trades
    const trades = await sdk.crossChainManager
        .calculateTrade(
            { blockchain: fromChain, address: tokenA }, 
            amountA,
            { blockchain: toChain, address: tokenB }
            );
    
    console.log(trades);
}

module.exports = {
    bridge_js
}