pragma solidity 0.5.6;

interface IMeshSwapExchange {
    
    function estimatePos(address token, uint amount) external view returns (uint);

    function estimateNeg(address token, uint amount) external view returns (uint);

    function exchangePos(address token, uint amount) external returns (uint);
    
    function exchangeNeg(address token, uint amount) external returns (uint);

    function token0() external view returns (address);

    function token1() external view returns (address);

}