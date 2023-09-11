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

// async function bridge_js(amountA, tokenA, tokenB, account, privateKey, node_url, network_name){

//     exports.configuration = {
//         rpcProviders: {
//             network_name: {
//                 rpcList: [node_url]
//             },
//         },
//     };

//     const sdk = await RubicSDK.SDK.createSDK(configuration);

//     var NODE_URL = node_url;
//     var provider = new Web3.providers.HttpProvider(NODE_URL);
//     var web3 = new Web3(provider);
//     var makerPrivateKey = privateKey;
//     var makerAddress = account;
//     var blockchainProvider = new LimitOrder.PrivateKeyProviderConnector(makerPrivateKey, web3);
//     var sdk = new fusion_sdk_1.FusionSDK({
//         url: 'https://fusion.1inch.io',
//         network: network_num,
//         blockchainProvider: blockchainProvider
//     });

//     const params = {
//         fromTokenAddress: tokenA,
//         toTokenAddress: tokenB,
//         amount: amountA,
//         walletAddress: makerAddress,
//     }

//     try {
//         const data = await sdk.placeOrder(params);
//         console.log(JSON.stringify(data));
//     } catch (error) {
//         console.error('Error:', error);
//         return null;
//     }
// }

module.exports = {
    // quote_js,
    bridge_js
}