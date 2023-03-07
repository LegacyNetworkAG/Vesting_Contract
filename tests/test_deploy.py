import pytest
from web3 import Web3
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
    
    _percent_per_milestone = [2000, 4000, 4000]
        
    # reverts because the address is a zero address
    # with brownie.reverts():
    #     vesting = VestingContract.deploy(_percent_per_milestone,
    #                                     '0x0000000000000000000000000000000000000000',
    #                                     {"from":legacy_network})


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

