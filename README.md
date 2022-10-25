## Basic functioning
- The constructor of the contract, among other things, initializes a **initLock** variable which  saves the unix time at which the contract was deployed or when the tokens are sent to the contract(depends on how we wish to do it). This time will serve as a timestamp of when the tokens where initially locked;
- Each month has a percentage of tokens (release_perc[month]) to be released in total
- Each month will be considered as 30 days = 2592000 sec. Since Solidity uses unix time and has a hard time fetching the month it is currently at, this is the most pratical way. However this can be changed to fit more detailed dates/requirements (for example using sucha library https://github.com/bokkypoobah/BokkyPooBahsDateTimeLibrary/blob/master/contracts/BokkyPooBahsDateTimeContract.sol)
- Every time the investor wants to withdraw tokens, the contract calls a separate function, **can_release_percent**, which uses the current time and the initLock time to calculate how much the investor can withdraw
- After the investor withdraws, the contract updates his investor[has_withdrawn] para meter;
- function can_release_percent():
$$ $$
    - Check how much time has elapsed how may percentage brakctes/months we have passed since the initLock;
$$ $$
    - For each bracket, claculate the percentage of tokens to be released in that period  
$$release\_perc[month]/2592000 * secondsInBracket.$$
    - Sum them all up in a variable called **total_release**
$$ $$
    - Get the percentage of released tokens he has already withdrawned,
$$has_withdrawn=investor[has\_withdrawn]$$
    - Get the percentage of tokens the investor can actually withdraw: 
$$able\_to\_release = total\_release - has\_withdrawn$$
    - Update 
$$investor[has\_withdrawn] = investor[has\_withdrawn] + able\_to\_release$$
    - return 
$$investor[tokens_promised]*$$
## Nomenclature

## Main functions (entry points)

## --TO DO--Documentation
- write the previous points in this file

## --TO DO--Code
- main functions -DONE
- main modifiers -DONE
- Percentage release logic  (theory) -DONE

## --TO DO--Testing
- Percentage release logic  (code)
- test the investor addition to the contract
- test constructor
- check safety of modifiers and functions
- see if variables can be simplified (maybe change some names to be more understandable)
- define the milestones and the payouts within the milestones
- test the whole system in a small unix timeframe