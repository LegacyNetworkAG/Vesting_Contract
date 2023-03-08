## --TO DO--Testing

- in test_newMulInvestors: test for addresses that aren't valid wallets and 0 address

# Tests

## Deploy:

- reverts because percentages don't add up to 100%
- reverts because the address is a zero address - TO DO!!!!
- regular pass and deploy

## newInvestor

## newMulInvestor

## release

# Gas difference between newMullInvestors and newInvestor for 1 new user:

But why do we need to functions to add new investors?
Because we want 2 things:

1. To be able to add a lot of new investors at once and with only one previous token transaction to the contract;
2. To add only one user at a time with a concurrent transaction, saving gas relative to the other method

## newMullInvestors:

from 0x5B38Da6a701c568545dCfcB03FcB875f56beddC4
to VestingContract.newMulInvestors(address[],address[],uint256[],uint256[],uint256) 0xd8b934580fcE35a11B58C6D73aDeE468a2833fa8
transaction cost 143310 gas
execution cost 120478 gas

## newInvestor:

from 0x5B38Da6a701c568545dCfcB03FcB875f56beddC4
to VestingContract.newInvestor(uint256,uint256,address) 0xd8b934580fcE35a11B58C6D73aDeE468a2833fa8
transaction cost 104337 gas
execution cost 82613 gas
