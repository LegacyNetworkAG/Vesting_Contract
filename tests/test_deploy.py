import pytest
import itertools
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

'''
Revert deployment
'''
def test_revertDeployment(tokenContract):

    # fetch the account
    legacy_network = accounts[0]

    _percent_per_milestone = [2000, 5000, 4000]
    _tokenAddress = tokenContract

    # reverts because perc_sum!=10000
    with brownie.reverts():
        vesting = VestingContract.deploy(_percent_per_milestone,
                                        _tokenAddress,
                                        {"from":legacy_network})
        
    # reverts because there are more than 120 months
    _percent_per_milestone = list(itertools.repeat(80,120))
    _percent_per_milestone.append(400)

    assert len(_percent_per_milestone) == 121
    assert sum(_percent_per_milestone) == 10_000
    with brownie.reverts():
        vesting = VestingContract.deploy(_percent_per_milestone,
                                        _tokenAddress,
                                        {"from":legacy_network})  
        
    # reverts because the address is a zero address
    _percent_per_milestone = [2000, 4000, 4000]
    with brownie.reverts():
        vesting = VestingContract.deploy(_percent_per_milestone,
                                        '0x0000000000000000000000000000000000000000',
                                        {"from":legacy_network})




'''
Regular deployment
'''
def test_regularDeployment(tokenContract):
    legacy_network = accounts[0]

    # parameters
    _percent_per_milestone = [2000, 4000, 4000] 
    _tokenAddress = tokenContract

    # should pass and deploy
    vesting = VestingContract.deploy(_percent_per_milestone,
                                        _tokenAddress,
                                        {"from":legacy_network})
    
    # print contract address
    print(f"Vesting contract deployed at {vesting}")
    return vesting

