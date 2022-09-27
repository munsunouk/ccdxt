interface IFactory {

    function owner() external view returns (address);

    function tokenToPool(address token0, address token1) external view returns (address);
    
    function poolExist(address) external view returns (bool);
}

