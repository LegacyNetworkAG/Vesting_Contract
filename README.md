## Basic functioning
- The constructor of the contract, among other things, initializes a **initLock** variable which  saves the unix time at which the contract was deployed or when the tokens are sent to the contract(depends on how we wish to do it). This time will serve as a timestamp of when the tokens where initially locked;
- Each month has a percentage of tokens (releasePerc[month]) to be released in total
- Each month will be considered as 30 days = 2592000 sec. Since Solidity uses unix time and has a hard time fetching the month it is currently at, this is the most pratical way. However this can be changed to fit more detailed dates/requirements (for example using sucha library https://github.com/bokkypoobah/BokkyPooBahsDateTimeLibrary/blob/master/contracts/BokkyPooBahsDateTimeContract.sol)
- Every time the investor wants to withdraw tokens, the contract calls a separate function, **can_release_percent**, which uses the current time and the initLock time to calculate how much the investor can withdraw
- After the investor withdraws, the contract updates his investor[hasWithdrawn] para meter;
- function can_release_percent():

    - Check how much time has elapsed how may percentage brakctes/months we have passed since the initLock;

    - For each bracket, claculate the percentage of tokens to be released in that period  
$$releasePerc[month]/2592000 * secondsInBracket.$$
    - Sum them all up in a variable called **totalRelease**
    - Get the percentage of released tokens he has already withdrawned,
$$hasWithdrawn=investor[hasWithdrawn]$$
    - Get the percentage of tokens the investor can actually withdraw: 
$$ableToRelease = totalRelease - hasWithdrawn$$
    - Update 
$$investor[hasWithdrawn] = investor[hasWithdrawn] + ableToRelease$$
    - return 
$$investor[tokensPromised]*ableToRelease$$
## Nomenclature

## Main functions (entry points)

## --TO DO--Documentation
- write the previous points in this file

## --TO DO--Code
- main functions -DONE
- main modifiers -DONE
- Percentage release logic  (theory) -DONE
- Percentage release logic  (code) -DONE
- Reviewed code and logic - Done
- Math appropriate -DONE
- See uint type along with the appropriate math -DONE
- Add delay time 3-6 months - DONE
- 
- Check that the contract has enough money while creating investor structs
## --TO DO--Testing
- test constructor -DONE
- check safety of modifiers and functions -DONE
- see if variables can be simplified (maybe change some names to be more understandable) -DONE
- define the milestones and the payouts within the milestones -DONE
- test the whole system in a small unix timeframe -DONE
- check math exploitations -DONE
- test the investor addition to the contract -DONE
