"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var sdk_1 = require("@traderjoe-xyz/sdk");
describe('Pair', function () {
    var USDT = new sdk_1.Token(sdk_1.ChainId.FUJI, '0x3763fB99d772D1D96571F39508e34489F400750c', 6, 'USDT', 'USDT Token');
    var JOE = new sdk_1.Token(sdk_1.ChainId.FUJI, '0x477Fd10Db0D80eAFb773cF623B258313C3739413', 18, 'JOE', 'JOE Token');
    var gUSDT = new sdk_1.Token(sdk_1.ChainId.ARB_GOERLI, '0xf450749aeA1c5feF27Ae0237C56FecC43f6bE244', 6, 'USDT', 'Tether Token');
    var gUSDC = new sdk_1.Token(sdk_1.ChainId.ARB_GOERLI, '0xb3482A25a12e5261b02E0acc5b96c656358a4086', 6, 'USDC', 'USD Coin');
    describe('constructor', function () {
        it('cannot be used for tokens on different chains', function () {
            expect(function () { return new sdk_1.Pair(new sdk_1.TokenAmount(USDT, '100'), new sdk_1.TokenAmount(sdk_1.WAVAX[sdk_1.ChainId.AVALANCHE], '100'), sdk_1.ChainId.FUJI); }).toThrow('CHAIN_IDS');
        });
    });
    describe('#getAddress', function () {
        it('returns the correct address', function () {
            expect(sdk_1.Pair.getAddress(USDT, JOE, sdk_1.ChainId.FUJI)).toEqual('0xd520cF33C013909AFc9Cf158D73F5460753B5ec4');
        });
        it('returns the correct address - arb goerli', function () {
            expect(sdk_1.Pair.getAddress(gUSDT, gUSDC, sdk_1.ChainId.ARB_GOERLI)).toEqual('0x682d5A31C8BDf110657d92F78467D196007749e3');
        });
    });
    describe('#token0', function () {
        it('always is the token that sorts before', function () {
            expect(new sdk_1.Pair(new sdk_1.TokenAmount(JOE, '100'), new sdk_1.TokenAmount(USDT, '100'), sdk_1.ChainId.FUJI).token0).toEqual(USDT);
            expect(new sdk_1.Pair(new sdk_1.TokenAmount(USDT, '100'), new sdk_1.TokenAmount(JOE, '100'), sdk_1.ChainId.FUJI).token0).toEqual(USDT);
        });
    });
    describe('#token1', function () {
        it('always is the token that sorts after', function () {
            expect(new sdk_1.Pair(new sdk_1.TokenAmount(JOE, '100'), new sdk_1.TokenAmount(USDT, '100'), sdk_1.ChainId.FUJI).token1).toEqual(JOE);
            expect(new sdk_1.Pair(new sdk_1.TokenAmount(USDT, '100'), new sdk_1.TokenAmount(JOE, '100'), sdk_1.ChainId.FUJI).token1).toEqual(JOE);
        });
    });
    describe('#reserve0', function () {
        it('always comes from the token that sorts before', function () {
            expect(new sdk_1.Pair(new sdk_1.TokenAmount(JOE, '100'), new sdk_1.TokenAmount(USDT, '101'), sdk_1.ChainId.FUJI).reserve0).toEqual(new sdk_1.TokenAmount(USDT, '101'));
            expect(new sdk_1.Pair(new sdk_1.TokenAmount(USDT, '101'), new sdk_1.TokenAmount(JOE, '100'), sdk_1.ChainId.FUJI).reserve0).toEqual(new sdk_1.TokenAmount(USDT, '101'));
        });
    });
    describe('#reserve1', function () {
        it('always comes from the token that sorts after', function () {
            expect(new sdk_1.Pair(new sdk_1.TokenAmount(JOE, '100'), new sdk_1.TokenAmount(USDT, '101'), sdk_1.ChainId.FUJI).reserve1).toEqual(new sdk_1.TokenAmount(JOE, '100'));
            expect(new sdk_1.Pair(new sdk_1.TokenAmount(USDT, '101'), new sdk_1.TokenAmount(JOE, '100'), sdk_1.ChainId.FUJI).reserve1).toEqual(new sdk_1.TokenAmount(JOE, '100'));
        });
    });
    describe('#token0Price', function () {
        it('returns price of token0 in terms of token1', function () {
            expect(new sdk_1.Pair(new sdk_1.TokenAmount(JOE, '101'), new sdk_1.TokenAmount(USDT, '100'), sdk_1.ChainId.FUJI).token0Price).toEqual(new sdk_1.Price(USDT, JOE, '100', '101'));
            expect(new sdk_1.Pair(new sdk_1.TokenAmount(USDT, '100'), new sdk_1.TokenAmount(JOE, '101'), sdk_1.ChainId.FUJI).token0Price).toEqual(new sdk_1.Price(USDT, JOE, '100', '101'));
        });
    });
    describe('#token1Price', function () {
        it('returns price of token1 in terms of token0', function () {
            expect(new sdk_1.Pair(new sdk_1.TokenAmount(JOE, '101'), new sdk_1.TokenAmount(USDT, '100'), sdk_1.ChainId.FUJI).token1Price).toEqual(new sdk_1.Price(JOE, USDT, '101', '100'));
            expect(new sdk_1.Pair(new sdk_1.TokenAmount(USDT, '100'), new sdk_1.TokenAmount(JOE, '101'), sdk_1.ChainId.FUJI).token1Price).toEqual(new sdk_1.Price(JOE, USDT, '101', '100'));
        });
    });
    describe('#priceOf', function () {
        var pair = new sdk_1.Pair(new sdk_1.TokenAmount(JOE, '101'), new sdk_1.TokenAmount(USDT, '100'), sdk_1.ChainId.FUJI);
        it('returns price of token in terms of other token', function () {
            expect(pair.priceOf(USDT)).toEqual(pair.token0Price);
            expect(pair.priceOf(JOE)).toEqual(pair.token1Price);
        });
        it('throws if invalid token', function () {
            expect(function () { return pair.priceOf(sdk_1.WAVAX[sdk_1.ChainId.FUJI]); }).toThrow('TOKEN');
        });
    });
    describe('#reserveOf', function () {
        it('returns reserves of the given token', function () {
            expect(new sdk_1.Pair(new sdk_1.TokenAmount(JOE, '100'), new sdk_1.TokenAmount(USDT, '101'), sdk_1.ChainId.FUJI).reserveOf(JOE)).toEqual(new sdk_1.TokenAmount(JOE, '100'));
            expect(new sdk_1.Pair(new sdk_1.TokenAmount(USDT, '101'), new sdk_1.TokenAmount(JOE, '100'), sdk_1.ChainId.FUJI).reserveOf(JOE)).toEqual(new sdk_1.TokenAmount(JOE, '100'));
        });
        it('throws if not in the pair', function () {
            expect(function () {
                return new sdk_1.Pair(new sdk_1.TokenAmount(USDT, '101'), new sdk_1.TokenAmount(JOE, '100'), sdk_1.ChainId.FUJI).reserveOf(sdk_1.WAVAX[sdk_1.ChainId.FUJI]);
            }).toThrow('TOKEN');
        });
    });
    describe('#chainId', function () {
        it('returns the token0 chainId', function () {
            expect(new sdk_1.Pair(new sdk_1.TokenAmount(JOE, '100'), new sdk_1.TokenAmount(USDT, '100'), sdk_1.ChainId.FUJI).chainId).toEqual(sdk_1.ChainId.FUJI);
            expect(new sdk_1.Pair(new sdk_1.TokenAmount(USDT, '100'), new sdk_1.TokenAmount(JOE, '100'), sdk_1.ChainId.FUJI).chainId).toEqual(sdk_1.ChainId.FUJI);
        });
    });
    describe('#involvesToken', function () {
        expect(new sdk_1.Pair(new sdk_1.TokenAmount(JOE, '100'), new sdk_1.TokenAmount(USDT, '100'), sdk_1.ChainId.FUJI).involvesToken(JOE)).toEqual(true);
        expect(new sdk_1.Pair(new sdk_1.TokenAmount(JOE, '100'), new sdk_1.TokenAmount(USDT, '100'), sdk_1.ChainId.FUJI).involvesToken(USDT)).toEqual(true);
        expect(new sdk_1.Pair(new sdk_1.TokenAmount(JOE, '100'), new sdk_1.TokenAmount(USDT, '100'), sdk_1.ChainId.FUJI).involvesToken(sdk_1.WAVAX[sdk_1.ChainId.FUJI])).toEqual(false);
    });
});
