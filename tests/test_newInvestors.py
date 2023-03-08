import pytest
import brownie
from brownie import accounts, chain, mock_token, VestingContract

@pytest.fixture
def tokenContract():
    # fetch the account
    account = accounts[0]

    # deploy contract
    token = mock_token.deploy({"from":account})
    # print contract address
    print(f"Token contract deployed at {token}")
    return token

@pytest.fixture
def vesting(tokenContract):

    # fetch the account
    legacy_network = accounts[0]
    
    _percent_per_milestone = [2000, 3500, 500, 1000, 2000, 1000]
    _tokenAddress = tokenContract
        
    # should pass and deploy
    vesting = VestingContract.deploy(_percent_per_milestone,
                                        _tokenAddress,
                                        {"from":legacy_network})
    print(f"Vesting contract deployed at {vesting}")
    return vesting


'''
Test revert scenarios for newInvestor
'''
def test_revertNewInv(tokenContract, vesting):
    # fetch the account
    legacy_network = accounts[0]
    Alice = accounts[1]
    Bob = accounts[2]
    Carol = accounts[3]
    David = accounts[4] 
    Hacker = accounts[5] 

    timeLock = 2592000 #1 month lock period

    # should revert because the Owner doesn't have enough funds
    amount=1000000*10**18
    with brownie.reverts():
        vesting.newInvestor(amount,
                                timeLock,
                                Alice,
                                {"from":legacy_network})

    # should revert because it is not the contract's owner who calls the function
    amount=100*10**18
    with brownie.reverts():
        vesting.newInvestor(amount,
                                timeLock,
                                Alice,
                                {"from":Hacker})
        
'''
Test regular scenarios for newMullInvestors
&
Test if it reverts if we try to add an existing vester address in a separate function call
'''
def test_regularNewMull(tokenContract, vesting):
    # Accounts
    legacy_network = accounts[0]
    Alice = accounts[1]
    Bob = accounts[2]


    # Variables
    amount=100*10**18
    timeLock = 2592000 #1 month lock period

    # should pass
    tokenContract.approve(vesting, 100*10**18, {"from": legacy_network})
    vesting.newInvestor(amount,
                                timeLock,
                                Alice,
                                {"from":legacy_network})
    tokenContract.approve(vesting, 100*10**18, {"from": legacy_network})
    vesting.newInvestor(amount,
                                timeLock,
                                Bob,
                                {"from":legacy_network})
    
    # should revert because the new investor is already vested
    with brownie.reverts():
        vesting.newInvestor(amount,
                                timeLock,
                                Alice,
                                {"from":legacy_network})