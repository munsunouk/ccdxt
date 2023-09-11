pragma solidity >=0.8.0;

interface IKIP7{
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);

    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function transfer(address recipient, uint256 amount) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
    function safeTransfer(address recipient, uint256 amount, bytes calldata data) external;
    function safeTransfer(address recipient, uint256 amount) external;
    function safeTransferFrom(address sender, address recipient, uint256 amount, bytes calldata data) external;
    function safeTransferFrom(address sender, address recipient, uint256 amount) external;

    // IKIP7Metadata (optional)
    function name() external view returns (string memory);
    function symbol() external view returns (string memory);
    function decimals() external view returns (uint8);

    // IKIP7Mintable (optional)
    function mint(address _to, uint256 _amount) external returns (bool);
    function isMinter(address _account) external view returns (bool);
    function addMinter(address _account) external;
    function renounceMinter() external;

    // IKIP7Burnable (optional)
    function burn(uint256 _amount) external;
    function burnFrom(address _account, uint256 _amount) external;

    // IKIP7Pausable (optional)
    event Paused(address _account);
    event Unpaused(address _account);

    function paused() external view returns (bool);
    function pause() external;
    function unpause() external;
    function isPauser(address _account) external view returns (bool);
    function addPauser(address _account) external;
    function renouncePauser() external;
}
