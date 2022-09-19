// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.8.0;

/// @notice Pool Factory interface.
interface IConcentratedLiquidityPoolFactory {
    /// @notice create and deploy a pool. if exists, revert.
    /// @param deployData abi.encode(address tokenA, address tokenB, uint24 swapFee, uint160 price, uint24 tickSpacing)
    function deployPool(bytes calldata deployData) external returns (address pool);

    /// @notice Return the address of the pool created with the given config data
    /// @param data abi.encode(address tokenA, address tokenB, uint24 swapFee, uint24 tickSpacing);
    function configAddress(bytes32 data) external returns (address pool);

    /// @notice Return whether the pool is created by the factory
    function isPool(address pool) external returns (bool ok);

    /// @notice Return the number of pools deployed from factory
    function totalPoolsCount() external view returns (uint256 total);

    /// @notice Return the address of pool by index
    function getPoolAddress(uint256 idx) external view returns (address pool);

    /// @notice Return the number of pools composed of two tokens
    function poolsCount(address token0, address token1) external view returns (uint256 count);

    /// @notice Return the list of pools composed of two tokens
    function getPools(
        address token0,
        address token1,
        uint256 startIndex,
        uint256 count
    ) external view returns (address[] memory pairPools);
}
