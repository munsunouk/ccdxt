pragma solidity 0.5.6;

interface IKlaySwapExchange {
    function balanceOf(address account) external view returns (uint256);

    function totalSupply() external view returns (uint256);

    function getCurrentPool() external view returns (uint, uint);

    function estimatePos(address token, uint amount) external view returns (uint);

    function estimateNeg(address token, uint amount) external view returns (uint);

    function tokenA() external view returns (address);

    function tokenB() external view returns (address);
}
