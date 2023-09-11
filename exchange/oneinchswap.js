"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var fusion_sdk_1 = require("@1inch/fusion-sdk");
var LimitOrder = require('@1inch/limit-order-protocol');
var Web3 = require('web3');

async function quote_js(amountA, tokenA, tokenB, account, network_num){

    const sdk = new fusion_sdk_1.FusionSDK({
        url: 'https://fusion.1inch.io',
        network: network_num
    })
    const params = {
        walletAddress: account,
        fromTokenAddress: tokenA,
        toTokenAddress: tokenB,
        amount: amountA,
        enableEstimate:false
    }
    
    try {
        const data = await sdk.getQuote(params);
        console.log(JSON.stringify(data));
    } catch (error) {
        console.error('Error:', error);
        return null;
    }
}

async function swap_js(amountA, tokenA, tokenB, account, privateKey, node_url, network_num){

    var NODE_URL = node_url;
    var provider = new Web3.providers.HttpProvider(NODE_URL);
    var web3 = new Web3(provider);
    var makerPrivateKey = privateKey;
    var makerAddress = account;
    var blockchainProvider = new LimitOrder.PrivateKeyProviderConnector(makerPrivateKey, web3);
    var sdk = new fusion_sdk_1.FusionSDK({
        url: 'https://fusion.1inch.io',
        network: network_num,
        blockchainProvider: blockchainProvider
    });

    const params = {
        fromTokenAddress: tokenA,
        toTokenAddress: tokenB,
        amount: amountA,
        walletAddress: makerAddress,
    }

    try {
        const data = await sdk.placeOrder(params);
        console.log(JSON.stringify(data));
    } catch (error) {
        console.error('Error:', error);
        return null;
    }
}

module.exports = {
    quote_js,
    swap_js
}