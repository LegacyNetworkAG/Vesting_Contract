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

        uint256 tokens_received;// amount of tokens the Investor has received

        uint256 tokens_promised;// amount of tokens the Investor is owed

        uint256 lock_start;// saves the date of the initial locking of the contract

        bool under250k_investor;// if true than it is an investor between 50k-250k, if false it is 250k+
    }

    //Variables
    address[] investor_address;// array with all the investor aaddresses
    address[] addresses_O50I;
    address[] addresses_O250I;
    uint256[] tokens_O50I;
    uint256[] tokens_O250I;
    uint256[] percent_per_milestone;//percentages per month that will be released (in basis points)
    uint256 initLock;// initial lock period 
    uint256 erc20Released;// total amount of released tokens
    uint256 numMilestones;// number of milestones (number of payments for each Investor)
    uint256 num_O50I;// number of under 50k token vested investors
    uint256 num_O250I;// number of over 50k token vested investors
    uint256 totalTokens_O50I;// total tokens promised to investors with 50k-250k tokens vested
    uint256 totalTokens_O250I;// total tokens promised to investors with more than 250k tokens vested
    address tokenAddress;// token address
    bool internal locked;   // boolean to prevent reentrancy

    //Functions
    /**
     * @dev Set the beneficiary, start timestamp and locking durations and amounts.
     */
    constructor(
        address[] memory _addresses_O50I,
        address[] memory _addresses_O250I,
        uint256[] memory _tokens_O50I,
        uint256[] memory _tokens_O250I,
        uint256[] memory _percent_per_milestone,
        uint256 _tokens_O50ITotal,// sum all the tokens for the investors with with 50k-250k tokens vested
        uint256 _tokens_O250ITotal,// ... more than 250k tokens
        address _tokenAddress
    ) {

        initLock = block.timestamp;

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
                                                block.timestamp, 
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
                                                block.timestamp, 
                                                false);

            // map the new Investor address to its struct
            walletToInvestor[_investor_address]=investor;

        }

        // establish token address
        tokenAddress = _tokenAddress;

        // establish the IERC20 for legacy token to contract interactions
        legacy_token = IERC20(_tokenAddress);

        // Initialize the reentrancy variable to not locked
        locked = false;

    }


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
        require(walletToInvestor[msg.sender].tokens_promised != 0, "Not an investor");
        _;
    }

    /**
     * @dev Release the tokens 
     *
     * Emits a {ERC20Released} event.
     */
    function release() public virtual noReentrant() onlyInvestor(){
        uint256 releasable = can_release_percent(msg.sender, uint256(block.timestamp));
        erc20Released += releasable;
        emit ERC20Released(tokenAddress, releasable);
        SafeERC20.safeTransfer(IERC20(tokenAddress), msg.sender, releasable);
        walletToInvestor[msg.sender].tokens_received += releasable;
    }


    /**
     * @dev Claculates and returns the amount of tokens that can be withdrawn, as function of milestones passed.
     * Updates the investor struct with the amount of tokens he has withdrawn.
     */
    function can_release_percent(address _callerAddress, uint256 timestamp) internal virtual returns (uint256) {

        // require that the investor has not already withdrawn everything
        require(walletToInvestor[msg.sender].tokens_received < walletToInvestor[msg.sender].tokens_promised, 
                "All tokens have been claimed");
        

        uint256 _current_time =timestamp;

        uint256 _can_release = 0;  //Sum them all up in a variable called **can_elease**
        uint256 _second_in_bracket = 0;

        uint _tokens_promised = walletToInvestor[msg.sender].tokens_promised;
        
        for(uint i = 1; i<= percent_per_milestone.length; i++){
        
            if(_current_time > (walletToInvestor[msg.sender].lock_start+2592000*i)){
                //Check how much time has elapsed how may percentage brakctes/months 
                    //we have passed since the initLock
                _second_in_bracket =2592000*i -2592000*(i-1);
                
                // For each bracket, claculate the the tokens to be released in that period  
                _can_release = _can_release + 
                    _tokens_promised * 
                    percent_per_milestone[i-1]/10000/2592000 * _second_in_bracket;// remember the percent_per 
                                                                                // milestone are percents multiplied by 1000 
                
            }else{
                //If the current time is in the middle of one of the months
                _second_in_bracket = _current_time - 2592000*(i-1)-walletToInvestor[msg.sender].lock_start;
                
                _can_release = _can_release + 
                    _tokens_promised * 
                    percent_per_milestone[i-1]/10000/2592000 * _second_in_bracket;

                break;
            }
        }


        //Get the quatity of tokens he has already withdrawned,
        uint256 _has_withdrawn = walletToInvestor[_callerAddress].tokens_received;

        //Get the amount of tokens the investor can actually withdraw: 
        uint256 _able_to_release = _can_release - _has_withdrawn;

        //Update 
        walletToInvestor[_callerAddress].tokens_received = walletToInvestor[_callerAddress].tokens_received 
                                                            + _able_to_release;
        //return 
        return  _able_to_release;
    }

    /**
     * @dev Adds a new Investor.
     */
    function new_Investor(uint256 _amount, address _newInvestor_address, bool _under250K) public {

        //require that the owner has enough legacy tokens to satisfy the promised tokens for locking
        require(legacy_token.balanceOf(_newInvestor_address)>= _amount, 
        "You don't have enough Legacy tokens for the price requirement.");

        require(walletToInvestor[_newInvestor_address].tokens_promised== 0, 
        "This address is already in the vesting contract.");

        // transfer the tokens to the contract
        legacy_token.transferFrom(_newInvestor_address, address(this), _amount);

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
                                                true);
        // push the new Investor structto the Investors arra
        walletToInvestor[_newInvestor_address]=investor;  
    }

    /**
     * @dev View function that an investor can use to see how many tokens he can withdraw
     */
    function view_can_release_percent() public view returns (uint256) {

        // require that the investor has not already withdrawn everything
        require(walletToInvestor[msg.sender].tokens_received < walletToInvestor[msg.sender].tokens_promised, 
                "All tokens have been claimed");
        

        uint256 _current_time = block.timestamp;

        uint256 _can_release = 0;  //Sum them all up in a variable called **can_elease**
        uint256 _second_in_bracket = 0;

        uint _tokens_promised = walletToInvestor[msg.sender].tokens_promised;
        
        for(uint i = 1; i<= percent_per_milestone.length; i++){
        
            if(_current_time > (walletToInvestor[msg.sender].lock_start+2592000*i)){
                //Check how much time has elapsed how may percentage brakctes/months 
                    //we have passed since the initLock
                _second_in_bracket =2592000*i -2592000*(i-1);
                
                // For each bracket, claculate the the tokens to be released in that period  
                _can_release = _can_release + 
                    _tokens_promised * 
                    percent_per_milestone[i-1]/10000/2592000 * _second_in_bracket;// remember the percent_per 
                                                                                // milestone are percents multiplied by 1000 
                
            }else{
                //If the current time is in the middle of one of the months
                _second_in_bracket = _current_time - 2592000*(i-1)-walletToInvestor[msg.sender].lock_start;
                
                _can_release = _can_release + 
                    _tokens_promised * 
                    percent_per_milestone[i-1]/10000/2592000 * _second_in_bracket;

                break;
            }
        }


        //Get the quatity of tokens he has already withdrawned,
        uint256 _has_withdrawn = walletToInvestor[msg.sender].tokens_received;

        //Get the amount of tokens the investor can actually withdraw: 
        uint256 _able_to_release = _can_release - _has_withdrawn;

        //return 
        return  _able_to_release;
    }

    /**
     * @dev View function to get contract balance
     */
    function contract_balance() public view returns (uint256) {
        return legacy_token.balanceOf(address(this));
    }

    function get_initLock() public view returns(uint256){
        return initLock;
    }
}