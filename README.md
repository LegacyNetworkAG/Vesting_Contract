# Tests

## Deploy:

- reverts because percentages don't add up to 100%
- reverts because the address is the zero address
- reverts because there are more than 120 months in the vesting percentages
- regular pass and deploy

## newInvestor

- should revert because the contract lacks funds
- should revert because it is not the contract's owner who calls the function
- regular pass
- should release all funds to Alice

## newMulInvestor

- should revert because the contract doesn't have enough funds
- reverts because the address is the zero address or the contracts own address (avoid locked funds)
- should revert because addresses and token amounts for O50 mismatch
- should revert because addresses and token amounts for O250 mismatch
- should revert because there are 2 equal users (Bob) in 050
- should revert because there are 2 equal users (Carol) in 0250
- should revert because there are 2 equal users (Alice) in between O50 and O250
- should revert because it is not the contract's owner who calls the function
- reverts because there are more than 180 addresses
- regular pass
- should revert if it tries to add an existing address as a new vester in a separate call
- should revert if we tried to add more users without sending more tokens to the contract
- should pass if we tried to add more users after sending more tokens to the contract

## release

- reverts because cliff (1 month) has not ended (for O250 only aka Carol and David)
- reverts because it is not a vester
- reverts because it has already withdrawn all promised tokens
- regular release before one month has passed after the cliff period and check if values are correct
- release after random time passage (> the cliff period but < than the vesting's end) and check if values are correct. This is done for several month time deltas
- release after the vesting is over for O50I but not O250I and check values
- release after the vesting is over for O250I and check values

# Gas difference between newMullInvestors and newInvestor for 1 new user:

But why do we need to functions to add new investors?
Because we want 2 things:

1. To be able to add a lot of new investors at once and with only one previous token transaction to the contract;
2. To add only one user at a time with a pervious transaction, saving gas relative to the other method

## newMullInvestors:

from 0x5B38Da6a701c568545dCfcB03FcB875f56beddC4
to VestingContract.newMulInvestors(address[],address[],uint256[],uint256[],uint256 0xd8b934580fcE35a11B58C6D73aDeE468a2833fa8
gas 164807 gas
transaction cost 143310 gas
execution cost 120478 gas

## newInvestor:

from 0x5B38Da6a701c568545dCfcB03FcB875f56beddC4
to VestingContract.newInvestor(uint256,uint256,address) 0xd8b934580fcE35a11B58C6D73aDeE468a2833fa8
gas 119988 gas
transaction cost 104337 gas
execution cost 82613 gas

# Gas

Average gas consumption for the tests
![Average gas](img/avg_gas.png)
The worst scenario (adding 180 users at one time using using newMulInvestors) gives
![Average gas](img/worstCase.png)
