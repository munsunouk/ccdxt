pragma solidity >=0.8.0;

interface IKlayswapRouter {
    function getPoolCount() external view returns (uint);

    function balanceOf(address account) external view returns (uint256);

    function getPoolAddress(uint idx) external view returns (address);

    function tokenToPool(address token1, address token2) external view returns (address);

    function getCurrentPool() external view returns (uint, uint);

    function poolExist(address poolAddr) external view returns (bool);

    function exchangeKlayPos(address token, uint256 amount, address[] calldata path) external payable;

    function exchangeKctPos(address tokenA, uint256 amountA, address tokenB, uint256 amountB, address[] calldata path) external;

}
