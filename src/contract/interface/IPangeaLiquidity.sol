// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.8.0;

/// @notice concentrated liquidity pool contract Structs.
interface IConcentratedLiquidityPoolStruct {
    struct Tick {
        /// @dev The highest tick below the current tick, pointer to the previous node in the linked list.
        int24 previousTick;
        /// @dev the lowest tick above the current tick, pointer to the next node in the linked list.
        int24 nextTick;
        /// @dev how much liquidity changes when the pool price crosses the tick
        uint128 liquidity;
        /// @dev the fee growth on the other side of the tick from the current tick in token0
        uint256 feeGrowthOutside0;
        /// @dev the fee growth on the other side of the tick from the current tick in token1
        uint256 feeGrowthOutside1;
        /// @dev the seconds spent per liquidity on the other side of the tick from the current tick
        uint160 secondsGrowthOutside;
    }
    struct Position {
        /// @dev the amount of liquidity in the position
        uint128 liquidity;
        /// @dev fee growth of token0 inside the tick range as of the last mint/burn/collect
        uint256 feeGrowthInside0Last;
        /// @dev fee growth of token1 inside the tick range as of the last mint/burn/collect
        uint256 feeGrowthInside1Last;
        /// @dev computed amount of token0 owed to the position as of the last mint/burn/collect
        uint128 feeOwed0;
        /// @dev computed amount of token1 owed to the position as of the last mint/burn/collect
        uint128 feeOwed1;
    }

    struct MintParams {
        /// @dev lowerOld previous lower tick
        int24 lowerOld;
        /// @dev lower The lower end of the tick range for the position
        int24 lower;
        /// @dev upperOld previous upper tick
        int24 upperOld;
        /// @dev upper The upper end of the tick range for the position
        int24 upper;
        /// @dev amount0Desired The amount of token0 to mint the given amount of liquidity
        uint128 amount0Desired;
        /// @dev amount1Desired The amount of token1 to mint the given amount of liquidity
        uint128 amount1Desired;
    }

    struct SwapCache {
        uint256 feeAmount;
        uint256 totalFeeAmount;
        uint256 protocolFee;
        uint256 swapFeeGrowthGlobalA;
        uint256 swapFeeGrowthGlobalB;
        uint256 currentPrice;
        uint256 currentLiquidity;
        uint256 input;
        int24 nextTickToCross;
    }
}

/// @notice Concentrated Liquidity Pool interface.
interface IConcentratedLiquidityPool is IConcentratedLiquidityPoolStruct {
    /// @notice The pool tick spacing
    /// @dev Ticks can only be used at multiples of this value, minimum of 1 and always positive
    /// e.g.: a tickSpacing of 3 means ticks can be created every 3rd tick, i.e., ..., -6, -3, 0, 3, 6, ...
    /// @dev Reference: tickSpacing of 100 -> 1% between ticks.
    function tickSpacing() external view returns (uint24);

    /// @dev 1000 corresponds to 0.1% fee. Fee is measured in pips.
    function swapFee() external view returns (uint24);

    /// @notice The first of the two tokens of the pool, sorted by address
    function token0() external view returns (address);

    /// @notice The second of the two tokens of the pool, sorted by address
    function token1() external view returns (address);

    /// @notice list of the tokens of the pool, sorted by address
    function getAssets() external view returns (address[] memory tokens);

    /// @notice Number of ticks on Pool, starts with two ticks (MIN_TICK & MAX_TICK)
    function totalTicks() external view returns (uint256);

    /// @notice The currently in range liquidity available to the poo
    // @dev This value has no relationship to the total liquidity across all ticks
    function liquidity() external view returns (uint128);

    /// @notice Sqrt of price aka. √(token1/token0), multiplied by 2^96.
    function price() external view returns (uint160);

    /// @notice Tick that is just below the current price.
    function nearestTick() external view returns (int24);

    /// @notice price and nearestTick
    function getPriceAndNearestTicks() external view returns (uint160 price, int24 nearestTick);

    /// @notice reserve of token0 and token1
    function getReserves() external view returns (uint128 reserve0, uint128 reserve1);

    /// @notice Look up information about a specific tick in the pool
    /// @param tick The tick to look up, the log base 1.0001 of price of the pool
    function ticks(int24 tick) external view returns (Tick memory);

    /// @notice Returns the information about a position
    /// @param owner owner of position, position is consisted of 3 elements, (owner / lower / upper)
    /// @param lower The lower tick of the position
    /// @param upper The upper tick of the position
    function positions(
        address owner,
        int24 lower,
        int24 upper
    ) external view returns (Position memory);

    /// @notice The fee growth of token0 collected per unit of liquidity for the entire life of the pool
    function feeGrowthGlobal0() external view returns (uint256);

    /// @notice The fee growth of token1 collected per unit of liquidity for the entire life of the pool
    function feeGrowthGlobal1() external view returns (uint256);

    /// @notice fee growth of token0 & token1 inside the given price range
    /// @param lower The lower tick of the position
    /// @param upper The upper tick of the position
    function rangeFeeGrowth(int24 lower, int24 upper) external view returns (uint256 feeGrowthInside0, uint256 feeGrowthInside1);

    /// @notice the address of factory contract
    function factory() external view returns (address);

    /// @notice Swaps one token for another. The router must prefund this contract and ensure there isn't too much slippage.
    /// @param data abi.encode(bool zeroForOne, address recipient)
    function swap(bytes memory data) external returns (uint256 amountOut);

    /// @notice Mints LP tokens - should be called via the Concentrated Liquidity pool manager contract.
    /// @param data MintParams(int24 lowerOld, int24 lower, int24 upperOld, int24 upper, uint128 amount0Desired, uint128 amount1Desired)
    function mint(MintParams memory data) external returns (uint256 liquidityMinted);

    /// @notice Receive token0 or token1 and pay it back with fee
    /// @param recipient The address which will receive the token0 and token1 amounts
    /// @param amount0 The amount of token0 to send
    /// @param amount1 The amount of token1 to send
    /// @param data Any data to be passed through to the callback
    function flash(
        address recipient,
        uint256 amount0,
        uint256 amount1,
        bytes calldata data
    ) external;

    /// @notice Burns LP tokens - should be called via the Concentrated Liquidity pool manager contract.
    /// @param lower The lower tick of the position
    /// @param upper The upper tick of the position
    /// @param amount The amount of liquidity to burn
    function burn(
        int24 lower,
        int24 upper,
        uint128 amount
    ) external returns (uint256 token0Amount, uint256 token1Amount);

    /// @notice Collects tokens owed to a position
    /// @param lower The lower tick of the position
    /// @param upper The upper tick of the position
    /// @param desiredToken0Fees How much token0 want be withdrawn from the fees owed
    /// @param desiredToken1Fees How much token1 want be withdrawn from the fees owed
    // @dev If desired fees exceeds the possible amount, only the possible amount will be returned.
    function collect(
        int24 lower,
        int24 upper,
        uint256 desiredToken0Fees,
        uint256 desiredToken1Fees
    ) external returns (uint256 token0Fees, uint256 token1Fees);

    /// @notice Returns the information about a seconds global growth and the timestamp of the observation
    /// @return secondGrowthGlobal the seconds per in range liquidity for the life of the pool as of the observation timestamp
    /// @return lastObservation The timestamp of the observation
    function getSecondsGrowthAndLastObservation() external view returns (uint160 secondGrowthGlobal, uint32 lastObservation);

    function collectProtocolFee() external returns (uint128, uint128);

    function getImmutables()
    external
    view
    returns (
        uint128 MAX_TICK_LIQUIDITY,
        uint24 tickSpacing,
        uint24 swapFee,
        address factory,
        address masterDeployer,
        address token0,
        address token1
    );
}
