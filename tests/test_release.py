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
    
    percentPerMilestone = [2000, 3500, 500, 1000, 2000, 1000]
    _tokenAddress = tokenContract
        
    # should pass and deploy
    vesting = VestingContract.deploy(percentPerMilestone,
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

def get_dict(test_keys, test_values):
    res = {}
    for key in test_keys:
        for value in test_values:
            res[key] = value
            test_values.remove(value)
            break
    return res   


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
Test release before the cliff has ended for the 0250I
'''
def test_cliffRelease(tokenContract, vesting, fundAndVest):
    # Accounts
    legacy_network = accounts[0]
    Alice = accounts[1]
    Bob = accounts[2]
    Carol = accounts[3]
    David = accounts[4] 

    # Variables
    secondsInMonth = 2592000   
    percentPerMilestone = [2000, 3500, 500, 1000, 2000, 1000]
    _addresses_O50I = [Alice, Bob]
    _addresses_O250I = [Carol, David]
    _tokens_O50I = [10*10**18, 20*10**18]
    _tokens_O250I = [100*10**18, 200*10**18]
    addrToAmountO50I = get_dict(_addresses_O50I, _tokens_O50I)# dict address->promised tokens
    addrToAmountO250I = get_dict(_addresses_O250I, _tokens_O250I)
    allowed_error = 10**3

    # release before one month has passed after the cliff period
    chain.mine(timedelta=secondsInMonth + secondsInMonth/2)# time passed since vesting = 1.5 months
    vesting.release({"from": Alice})
    assert (tokenContract.balanceOf(Alice, {'from': Alice}) - 
            (percentPerMilestone[0] + percentPerMilestone[1]*0.5) * addrToAmountO50I[Alice]) < allowed_error
    vesting.release({"from": Bob})
    assert (tokenContract.balanceOf(Bob, {'from': Bob}) - 
            (percentPerMilestone[0] + percentPerMilestone[1]*0.5) * addrToAmountO50I[Bob]) < allowed_error
    vesting.release({"from": Carol})
    assert (tokenContract.balanceOf(Carol, {'from': Carol}) - 
            (percentPerMilestone[0]*0.5) * addrToAmountO250I[Carol]) < allowed_error
    vesting.release({"from": David})
    assert (tokenContract.balanceOf(David, {'from': David}) - 
            (percentPerMilestone[0]*0.5) * addrToAmountO250I[David]) < allowed_error


'''
Test release regular situations, after the cliff and before the vest ending
'''
@pytest.mark.parametrize('month', [1, 2, 3, 4])
def test_regularRelease(tokenContract, vesting, fundAndVest, month):
    # Accounts
    legacy_network = accounts[0]
    Alice = accounts[1]
    Bob = accounts[2]
    Carol = accounts[3]
    David = accounts[4] 

    # Variables
    secondsInMonth = 2592000   
    percentPerMilestone = [2000, 3500, 500, 1000, 2000, 1000]
    _addresses_O50I = [Alice, Bob]
    _addresses_O250I = [Carol, David]
    _tokens_O50I = [10*10**18, 20*10**18]
    _tokens_O250I = [100*10**18, 200*10**18]
    addrToAmountO50I = get_dict(_addresses_O50I, _tokens_O50I)# dict address->promised tokens
    addrToAmountO250I = get_dict(_addresses_O250I, _tokens_O250I)
    allowed_error = 10**3

    # release after random time passage (> the cliff period but < than the vesting's end)
    chain.mine(timedelta=secondsInMonth*month)
    vesting.release({"from": Alice})
    assert (tokenContract.balanceOf(Alice, {'from': Alice}) - 
            (sum(percentPerMilestone[0:month]) + percentPerMilestone[month+1]*0.5) * addrToAmountO50I[Alice]) < allowed_error
    vesting.release({"from": Bob})
    assert (tokenContract.balanceOf(Bob, {'from': Bob}) - 
            (sum(percentPerMilestone[0:month]) + percentPerMilestone[month+1]*0.5) * addrToAmountO50I[Bob]) < allowed_error
    vesting.release({"from": Carol})
    assert (tokenContract.balanceOf(Carol, {'from': Carol}) - 
            (sum(percentPerMilestone[0:month-1]) + percentPerMilestone[month]*0.5) * addrToAmountO250I[Carol]) < allowed_error
    vesting.release({"from": David})
    assert (tokenContract.balanceOf(David, {'from': David}) - 
            (sum(percentPerMilestone[0:month-1]) + percentPerMilestone[month]*0.5) * addrToAmountO250I[David]) < allowed_error
    
'''
Test the release when the vest periods are over (make sure users get full funds)
'''
def test_vestOverRelease(tokenContract, vesting, fundAndVest):
    # Accounts
    legacy_network = accounts[0]
    Alice = accounts[1]
    Bob = accounts[2]
    Carol = accounts[3]
    David = accounts[4] 

    # Variables
    secondsInMonth = 2592000   
    percentPerMilestone = [2000, 3500, 500, 1000, 2000, 1000]
    _addresses_O50I = [Alice, Bob]
    _addresses_O250I = [Carol, David]
    _tokens_O50I = [10*10**18, 20*10**18]
    _tokens_O250I = [100*10**18, 200*10**18]
    addrToAmountO50I = get_dict(_addresses_O50I, _tokens_O50I)# dict address->promised tokens
    addrToAmountO250I = get_dict(_addresses_O250I, _tokens_O250I)
    allowed_error = 10**3

    # release after the vesting is over for 050
    chain.mine(timedelta=secondsInMonth*6)# time passed since vesting = 6 months
    vesting.release({"from": Alice})
    assert tokenContract.balanceOf(Alice, {'from': Alice}) ==  addrToAmountO50I[Alice]
    vesting.release({"from": Bob})
    assert tokenContract.balanceOf(Bob, {'from': Bob}) ==  addrToAmountO50I[Bob]

    vesting.release({"from": Carol})
    assert tokenContract.balanceOf(Carol, {'from': Carol}) !=  addrToAmountO250I[Carol]
    vesting.release({"from": David})
    assert tokenContract.balanceOf(David, {'from': David}) !=  addrToAmountO250I[David]

    # release after the vesting is over for 0250
    chain.mine(timedelta=secondsInMonth)# time passed since vesting = 7 months
    with brownie.reverts():
        vesting.release({"from": Alice})
    assert tokenContract.balanceOf(Alice, {'from': Alice}) ==  addrToAmountO50I[Alice]
    with brownie.reverts():
        vesting.release({"from": Bob})
    assert tokenContract.balanceOf(Bob, {'from': Bob}) ==  addrToAmountO50I[Bob]

    vesting.release({"from": Carol})
    assert tokenContract.balanceOf(Carol, {'from': Carol}) ==  addrToAmountO250I[Carol]
    vesting.release({"from": David})
    assert tokenContract.balanceOf(David, {'from': David}) ==  addrToAmountO250I[David]