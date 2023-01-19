// SPDX-License-Identifier: MIT
// OpenZeppelin Contracts (last updated v4.7.0) (finance/LockContract.sol)
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/Address.sol";
import "@openzeppelin/contracts/utils/Context.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title LockContract
 * @dev This contract handles the vesting of a ERC20 tokens for a given beneficiary. Custody of the _token amount
 * can be given to this contract, which will release the _token to the beneficiary following a given schedule.
 * The vesting schedule is established by an array of basis point. Each index of that array
 * corresponds to a month after the vesting period starts (aka after the locking period is over)
 */
contract VestingContract is Context, Ownable {
    //Token
    IERC20 public legacy_token;

    //Events
    event ERC20Released(address indexed _token, uint256 amount);

    //Mappings
    mapping(address => Investor) public walletToInvestor;

    //Structs
    struct Investor {
        uint256 tokens_received; // amount of tokens the Investor has received
        uint256 tokens_promised; // amount of tokens the Investor is owed
        uint256 vesting_start; // saves the date in which the locking period ends
        //and the vesting (token releases) starts
    }

    //Variables
    address[] investor_address; // array with all the investor aaddresses
    uint256[] percent_per_milestone; //percentages per month that will be released (in basis points)
    uint256 erc20Released; // total amount of released tokens
    uint256 numMilestones; // number of milestones (number of payments for each Investor)
    uint256 totalTokens_O50I; // total tokens promised to investors with 50k-250ks
    uint256 totalTokens_O250I; // total tokens promised to investors with more than 250ks
    address tokenAddress; // token address
    bool internal locked; // boolean to prevent reentrancy

    // Modifiers
    /**
     * @dev Prevents reentrancy
     */
    modifier noReentrant() {
        require(!locked, "No re-entrancy");
        locked = true;
        _;
        locked = false;
    }

    /**
     * @dev Only investors can call functions
     */
    modifier onlyInvestor() {
        require(
            walletToInvestor[msg.sender].tokens_promised != 0,
            "Not an investor"
        );
        _;
    }

    //Functions
    /**
     * @dev Set the beneficiary, start timestamp and locking durations and amounts.
     */
    constructor(
        address[] memory _addresses_O50I, // array with the addresses of the investors with 50k to 250ks
        address[] memory _addresses_O250I, // ... more than 250ks
        uint256[] memory _tokens_O50I, // array with the token amount to be to the equivalent
        // indexed address in _addresses_O50I
        uint256[] memory _tokens_O250I, // ... addres in _addresses_O250I
        uint256[] memory _percent_per_milestone, // has the basis point values of the percentages
        // of tokens that should be released in total in
        // the indexed month
        uint256 _timeLock_O250I, // ... more than 250ks
        address _tokenAddress // address of the token to be used
    ) {
        // percentage of tokens an investor can withdraw at each milestone
        percent_per_milestone = _percent_per_milestone;

        // number of investors with...
        uint256 _num_O50I = _addresses_O50I.length; // with 50k-250ks
        uint256 _num_O250I = _addresses_O250I.length; // more than 250ks

        // create an Investor struct for each investor with less than 50ks
        for (uint256 i = 0; i < _num_O50I; i++) {
            // get the amount of tokens and the address correpsonding to this investor
            address _investor_address = _addresses_O50I[i];
            uint256 _investor_tokens = _tokens_O50I[i];

            // create the new Investor struct
            Investor memory investor = Investor(
                0,
                _investor_tokens,
                block.timestamp
            );

            // map the new Investor address to its struct
            walletToInvestor[_investor_address] = investor;
        }

        // create an Investor struct for each investor with more than 250ks
        for (uint256 i = 0; i < _num_O250I; i++) {
            // get the amount of tokens and the address correpsonding to this investor
            address _investor_address = _addresses_O250I[i];
            uint256 _investor_tokens = _tokens_O250I[i];

            // create the new Investor struct
            Investor memory investor = Investor(
                0,
                _investor_tokens,
                block.timestamp + _timeLock_O250I
            );

            // map the new Investor address to its struct
            walletToInvestor[_investor_address] = investor;
        }

        // establish token address
        tokenAddress = _tokenAddress;

        // establish the IERC20 for legacy token to contract interactions
        legacy_token = IERC20(_tokenAddress);

        // Initialize the reentrancy variable to not locked
        locked = false;
    }

    /**
     * @dev Calculates and returns the amount of tokens that can be withdrawn,
     * as function of milestones passed.
     */
    function can_release_percent(address _callerAddress)
        public
        view
        returns (uint256)
    {
        // get the quatity of tokens he has already withdrawned,
        uint256 _has_withdrawn = walletToInvestor[_callerAddress]
            .tokens_received;
        // gets the investors promised tokens
        uint256 _tokens_promised = walletToInvestor[_callerAddress]
            .tokens_promised;

        // require that the investor has not already withdrawn everything
        require(
            _has_withdrawn < _tokens_promised,
            "All tokens have been claimed"
        );

        // gets the current time
        uint256 _current_time = uint256(block.timestamp);
        // gets the time in which the investors vesting starts
        uint256 _vesting_start = walletToInvestor[_callerAddress].vesting_start;

        // require that the first month of vesting has passed (and as consequence, checks if the lock
        //period has passed already)
        require(
            _current_time > _vesting_start,
            "First month of vesting has not passed"
        );

        // will save the amount that is calculated that can be released
        uint256 _can_release = 0;
        // saves the seconds the investor has spent vesting in each bracket, to allow the token withdraw calc
        uint256 _second_in_bracket = 0;

        //Loop through every month until we reach the one the  vesting of this investor is currently on
        for (uint256 i = 1; i <= percent_per_milestone.length; i++) {
            // if the time the investor has been vesting is bigger than i month
            if (_current_time > (_vesting_start + 2592000 * i)) {
                // check how much time has elapsed how may percentage brakctes/months
                //we have passed since the initLock
                _second_in_bracket = 2592000;

                // for each bracket, claculate the the tokens to be released in that period
                _can_release =
                    _can_release +
                    ((_tokens_promised * percent_per_milestone[i - 1]) /
                        10000 /
                        2592000) *
                    _second_in_bracket; // remember the percent_per
                // milestone are percents multiplied by 1000
            } else {
                //If the current time is in the middle of one of the months
                _second_in_bracket =
                    _current_time -
                    2592000 *
                    (i - 1) -
                    _vesting_start;

                _can_release =
                    _can_release +
                    ((_tokens_promised * percent_per_milestone[i - 1]) /
                        10000 /
                        2592000) *
                    _second_in_bracket;

                break;
            }
        }

        // get the amount of tokens the investor can actually withdraw:
        return _can_release - _has_withdrawn;
    }

    /**
     * @dev Release the tokens
     *
     * Emits a {ERC20Released} event.
     */
    function release() public virtual noReentrant onlyInvestor {
        // gets the amount of tokens the investor can withdraw
        uint256 releasable = can_release_percent(msg.sender);

        // transfers the tokens to the investor
        bool success = legacy_token.transfer(msg.sender, releasable);
        require(success, "Failed to release tokens.");

        // adds that amount to the total released amount
        erc20Released += releasable;

        // emits an event
        emit ERC20Released(tokenAddress, releasable);

        // updates the investors struct to reflect the withdraw
        walletToInvestor[msg.sender].tokens_received += releasable;
    }

    /**
     * @dev Adds a new Investor.
     */
    function new_Investor(
        uint256 _amount,
        address _newInvestor_address,
        uint256 _timeLock
    ) public onlyOwner {
        // the investor should not already by locked
        require(
            walletToInvestor[_newInvestor_address].tokens_promised == 0,
            "This address is already in the vesting contract."
        );

        // transfer the tokens to the contract
        bool success = legacy_token.transfer(address(this), _amount);
        require(success, "Failed to deposit tokens.");

        // create the new Investor struc
        Investor memory investor = Investor(
            0,
            _amount,
            block.timestamp + _timeLock
        );

        // push the new Investor struct to the Investors array
        walletToInvestor[_newInvestor_address] = investor;
    }
}
