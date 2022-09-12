pragma solidity 0.5.6;

interface IExchange {
    function estimatePos(address token, uint amount) external view returns (uint);
    function estimateNeg(address token, uint amount) external view returns (uint);
    function getCurrentPool() external view returns (uint, uint);
    function exchangePos(address token, uint amount) external returns (uint);
    function exchangeNeg(address token, uint amount) external returns (uint);

    function addTokenLiquidityWithLimit(uint amount0, uint amount1, uint minAmount0, uint minAmount1, address user) external returns (uint real0, uint real1, uint amountLP);
    function removeLiquidityWithLimit(uint amount, uint minAmount0, uint minAmount1, address user) external returns (uint, uint);
    function removeLiquidityWithLimitETH(uint amount, uint minAmount0, uint minAmount1, address user) external returns (uint, uint);
    function claimReward(address user) external;

    function permit(address owner, address spender, uint value, uint deadline, uint8 v, bytes32 r, bytes32 s) external;
    function token0() external view returns (address);
    function token1() external view returns (address);
    function getReserves() external view returns (uint112 _reserve0, uint112 _reserve1, uint32 _blockTimestampLast);

}