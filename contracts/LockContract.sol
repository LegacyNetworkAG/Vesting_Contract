// SPDX-License-Identifier: MIT
// OpenZeppelin Contracts (last updated v4.7.0) (finance/LockContract.sol)
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/Address.sol";
import "@openzeppelin/contracts/utils/Context.sol";
import "@openzeppelin/contracts/utils/math/Math.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title LockContract
 * @dev This contract handles the vesting of a ERC20 tokens for a given beneficiary. Custody of the _token amount
 * can be given to this contract, which will release the _token to the beneficiary following a given schedule.
 * The vesting schedule is established by a key->value pair in the form of _duration->_amounts. This two arrays
 * have the same length and are iterated by the _milestone variable
 */
contract LockContract is Context, Ownable  {

    //Token
    IERC20 public legacy_token;

    //Events
    event ERC20Released(address indexed _token, uint256 amount);

    //Mappings
    mapping(address => Investor) public walletToInvestor;

    //Structs
    struct Investor {
        address investor_address;// probably can take it out

        uint256 received_tokens;// amount of tokens the Investor has received

        uint256 tokens_promised;// amount of tokens the Investor is owed

        uint64 lock_start;// saves the date of the initial locking of the contract

        uint8 can_withdraw;// percentage of his tokens the investor can withdraw at the moment

        uint8 has_withdrawn;// percentage of tokens th einvestor has withdrawn

        bool under50k_investor;/* 
                          saves gas by id'ing each Investor as _under50k/true (the original locked Investor) 
                          or new/false (new employes). This way we can just save the durations and amounts
                          in two single variables in the contract instead of saving them for each _under50k Investor
                         */
    }

    //Variables
    address[] investor_address;// array with all the investor aaddresses
    address[] addresses_O50I;
    address[] addresses_O250I;
    uint256[] tokens_O50I;
    uint256[] tokens_O250I;
    uint8[] percent_per_milestone;
    uint256 initLock;// initial lock period 
    uint256 erc20Released;// total amount of released tokens
    uint256 numMilestones;// number of milestones (number of payments for each Investor)
    uint256 num_O50I;// number of under 50k token vested investors
    uint256 num_O250I;// number of over 50k token vested investors
    uint256 totalTokens_O50I;// total tokens promised to investors with 50k-250k tokens vested
    uint256 totalTokens_O250I;// total tokens promised to investors with more than 250k tokens vested
    address token;// token address

    //Functions
    /**
     * @dev Set the beneficiary, start timestamp and locking durations and amounts.
     */
    constructor(
        IERC20 _legacy_token,
        address[] memory _addresses_O50I,
        address[] memory _addresses_O250I,
        uint256[] memory _tokens_O50I,
        uint256[] memory _tokens_O250I,
        uint8[] memory _percent_per_milestone,
        uint256 _numMilestones,
        uint256 _initLock,
        uint256 _tokens_O50ITotal,// sum all the tokens for the investors with with 50k-250k tokens vested
        uint256 _tokens_O250ITotal,// ... more than 250k tokens
        address _tokenAdress
    ) {

        legacy_token=_legacy_token;
        // number of milestones
        numMilestones = _numMilestones;

        // percentage of tokens an investor can withdraw at each milestone
        percent_per_milestone = _percent_per_milestone;

        // number of investors with...
        num_O50I = _addresses_O50I.length;// with 50k-250k tokens vested
        num_O250I = _addresses_O250I.length;// more than 250k tokens vested

        // array of addresses of investors with ...
        addresses_O50I= _addresses_O50I;// with 50k-250k tokens vested
        addresses_O250I= _addresses_O250I;// more than 250k tokens vested

        // array of tokens promised to investors with ...
        tokens_O50I = _tokens_O50I;// with 50k-250k tokens vested
        tokens_O250I = _tokens_O250I;// more than 250k tokens vested

        // total tokens promised to investors with ...
        totalTokens_O50I = _tokens_O50ITotal;// with 50k-250k tokens vested
        totalTokens_O250I = _tokens_O250ITotal;// more than 250k tokens vested

        // create an Investor struct for each investor with less than 50k tokens
        for (uint i=0; i<num_O50I; i++){

            // Investor address can't be the zero address
            require(addresses_O50I[i] != address(0),
                     "Constructor: locked Investor address is zero address");

            // get the amount of tokens and the address correpsonding to this investor
            address _investor_address = addresses_O50I[i];
            uint256 _investor_tokens = tokens_O50I[i];
           
            // create the new Investor struct
            Investor memory investor = Investor(_investor_address, 
                                                0, 
                                                _investor_tokens, 
                                                uint64(block.timestamp), 
                                                0, 
                                                0,
                                                true);

            // map the new Investor address to its struct
            walletToInvestor[_investor_address]=investor;

        }

        // create an Investor struct for each investor with more than 250k tokens
        for (uint i=0; i<num_O250I; i++){

            // Investor address can't be the zero address
            require(addresses_O250I[i] != address(0),
                     "Constructor: locked Investor address is zero address");

            // get the amount of tokens and the address correpsonding to this investor
            address _investor_address = addresses_O250I[i];
            uint256 _investor_tokens = tokens_O250I[i];
           
            // create the new Investor struct
            Investor memory investor = Investor(_investor_address, 
                                                0, 
                                                _investor_tokens, 
                                                uint64(block.timestamp), 
                                                0, 
                                                0,
                                                true);

            // map the new Investor address to its struct
            walletToInvestor[_investor_address]=investor;

        }
        // establish token address
        token = _tokenAdress;
        legacy_token = _legacy_token;

        // establish the durations periods 
        initLock = _initLock;
    }


    /**
     * @dev Calculates the date of the next milestone (used to see if the milestone has passed or not)
     * --TO DO
     */
    function get_date(address _callerAddress) public view virtual returns (uint256) {

        // get the last milestone the Investor received
        //uint16 currentMileStone = walletToInvestor[_callerAddress].milestone;
        // get the time the lock period began for this Investor
        uint64 lock_start = walletToInvestor[_callerAddress].lock_start;

        /* the date is equal to the locking start date + the lock 
         time (2 years) + a month for each milestone already retrived
        */
        uint256 milestone_date = lock_start + initLock+ (30 days)*currentMileStone;
        
        // return the date of the next milestone 
        return milestone_date;
    }


    /**
     * @dev Release the tokens according to milestone passage.
     *
     * Emits a {ERC20Released} event.
     */
    function release() public virtual{
        uint256 releasable = _vestingSchedule(msg.sender, uint64(block.timestamp));
        erc20Released += releasable;
        emit ERC20Released(token, releasable);
        SafeERC20.safeTransfer(IERC20(token), msg.sender, releasable);
        walletToInvestor[msg.sender].received_tokens += releasable;
    }


    /**
     * @dev This returns the amount of tokens that can be withdrawn, as function of milestones passed.
     */
    function _vestingSchedule(address _callerAddress, uint64 timestamp) internal virtual returns (uint256) {
        // get the last milestone the Investor received
        uint16 currentMileStone = walletToInvestor[_callerAddress].milestone;

        require(currentMileStone < numMilestones, "All milestone rewards have been claimed");

        //If the time is superior to the current milestone duration...
        if (timestamp > get_date(_callerAddress)) {
            //...we save the the amount we can withdraw in this milestone.

            // get the amount of tokens that belong to each Investor
            uint256 can_withdraw = walletToInvestor[_callerAddress].tokens_promised/(numMilestones);

            //Increment the milestone of a particular Investor (if it is not the last milestone)
            walletToInvestor[_callerAddress].milestone = walletToInvestor[_callerAddress].milestone+1;

            //Return the amount to withdraw this milestone
            return can_withdraw;

        } else {
            return 0;
        }
    }

    /**
     * @dev Adds a new Investor.
     */
    function new_Investor(uint256 _amount, address _newInvestor_address, bool _under250K) public onlyOwner{

        if(_under250K){
            addresses_O50I.push(_newInvestor_address);
            tokens_O50I.push(_amount);
        }else{
            addresses_O250I.push();
            tokens_O250I.push(_amount);
        }

        // create the new Investor struc
        Investor memory investor = Investor(_newInvestor_address, 
                                                0, 
                                                _amount, 
                                                uint64(block.timestamp),
                                                0, 
                                                true);
        // push the new Investor structto the Investors arra
        walletToInvestor[_newInvestor_address]=investor;  
    }
}