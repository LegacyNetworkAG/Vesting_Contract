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


@pytest.fixture
def fundAndVest(tokenContract, vesting):
    # fetch the account
    legacy_network = accounts[0]
    Alice = accounts[1]
    Bob = accounts[2]
    Carol = accounts[3]
    David = accounts[4]  

    #Fund contract
    tokenContract.transfer(vesting,
                            330*10**18,
                            {"from": legacy_network})
    _addresses_O50I = [Alice, Bob]
    _addresses_O250I = [Carol, David]
    _tokens_O50I = [10*10**18, 20*10**18]
    _tokens_O250I = [100*10**18, 200*10**18]
    _timeLock_O250I = 2592000 #1 month lock period
    vesting.newMulInvestors(_addresses_O50I,
                                        _addresses_O250I,
                                        _tokens_O50I, 
                                        _tokens_O250I,
                                        _timeLock_O250I,
                                        {"from":legacy_network})
    

'''
Test release revert situations
'''
def test_revertRelease(tokenContract, vesting, fundAndVest):
    # fetch the account
    legacy_network = accounts[0]
    Alice = accounts[1]
    Bob = accounts[2]
    Carol = accounts[3]
    David = accounts[4]
    Hacker = accounts[5]
    secondsInMonth = 2592000  

    # reverts because cliff (1 month) has not ended (for O250 only aka Carol and David)
    chain.mine(timedelta=secondsInMonth/2)# time passed since vesting = 1/2 month

    vesting.release({"from": Alice})
    vesting.release({"from": Bob})
    with brownie.reverts():
        vesting.release({"from": Carol})
    with brownie.reverts():
        vesting.release({"from": David})

    # reverts because it is not a vester
    chain.mine(timedelta=secondsInMonth*2)# time passed since vesting = 2,5 month
    with brownie.reverts():
        vesting.release({"from": Hacker})
    
    # reverts because it has already withdrawn all promised tokens
    chain.mine(timedelta=secondsInMonth*5)# time passed since vesting = 7.5 month > vesting+cliff=7months
    vesting.release({"from": Alice})
    assert tokenContract.balanceOf(Alice, {"from": Alice}) == 10*10**18
    with brownie.reverts():
        vesting.release({"from": Alice})
'''
Test release regular situations
'''
def test_regularRelease(tokenContract, vesting, fundAndVest):
    # fetch the account
    legacy_network = accounts[0]
    Alice = accounts[1]
    Bob = accounts[2]
    Carol = accounts[3]
    David = accounts[4]  

    # release before on month has passed after the cliff period
    # release after random time passage (> the cliff period but < than the vesting's end)
    # release after the vesting is over