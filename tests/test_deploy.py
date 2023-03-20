from eth_utils.abi import function_abi_to_4byte_selector, collapse_if_tuple
from brownie import accounts, chain, mock_token, VestingContract
import itertools
import brownie
import pytest
import json

#SETUP FUNCTIONS
@pytest.fixture
def tokenContract():
    # fetch the account
    account = accounts[0]

    # deploy contract
    token = mock_token.deploy({"from":account})
    # print contract address
    print(f"Token contract deployed at {token}")
    return token

#CALLABLE FUNCTIONS
def encode_custom_error(contract_name, err_name, params):
    with open("build/Contracts/"+contract_name+".json") as f:
        info_json = json.load(f)
    contract_abi = info_json["abi"]
    for error in [abi for abi in contract_abi if abi["type"] == "error"]:
        # Get error signature components
        name = error["name"]
        data_types = [collapse_if_tuple(abi_input) for abi_input in error.get("inputs", [])]
        error_signature_hex = function_abi_to_4byte_selector(error).hex()
        if err_name == name:
            encoded_params = ''
            for param in params:
                val = "{0:#0{1}x}".format(param,66)
                val = val[2:]
                encoded_params = encoded_params + val
            return('typed error: 0x'+error_signature_hex+encoded_params)
'''
Revert deployment
'''
def test_revertDeployment(tokenContract):

    # fetch the account
    legacy_network = accounts[0]

    _percent_per_milestone = [2000, 5000, 4000]
    _tokenAddress = tokenContract

    # reverts because perc_sum!=10000
    with brownie.reverts(encode_custom_error('VestingContract', 'percSumIncorrect', [11_000])):
        vesting = VestingContract.deploy(_percent_per_milestone,
                                        _tokenAddress,
                                        {"from":legacy_network})
        
    # reverts because there are more than 120 months
    _percent_per_milestone = list(itertools.repeat(80,120))
    _percent_per_milestone.append(400)

    assert len(_percent_per_milestone) == 121
    assert sum(_percent_per_milestone) == 10_000
    with brownie.reverts(encode_custom_error('VestingContract', 'inputTooLarge', [120, 121])):
        vesting = VestingContract.deploy(_percent_per_milestone,
                                        _tokenAddress,
                                        {"from":legacy_network})  
        
    # reverts because the address is a zero address
    _percent_per_milestone = [2000, 4000, 4000]
    with brownie.reverts(encode_custom_error('VestingContract', 'invalidAddress', [])):
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

