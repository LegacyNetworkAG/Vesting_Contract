from eth_utils.abi import function_abi_to_4byte_selector, collapse_if_tuple
from brownie import accounts, chain, mock_token, VestingContract
from random import randint
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
                if(type(param)==str):
                    return('typed error: 0x'+error_signature_hex+param[2:].lower().zfill(64))
                val = "{0:#0{1}x}".format(param,66)
                val = val[2:]
                encoded_params = encoded_params + val
            return('typed error: 0x'+error_signature_hex+encoded_params)

'''
Test revert scenarios for newMullInvestors
'''
def test_revertNewMull(tokenContract, vesting):
    # fetch the account
    legacy_network = accounts[0]

    _timeLock_O250I = 2592000 #1 month lock period

    tokenContract.transfer(vesting,
                            300*10**18,
                            {"from": legacy_network})# contract has enough funds now
        

    _addresses_O50I = []
    for _ in range(90):
        new_acc = accounts.add()
        _addresses_O50I.append(new_acc)

    _addresses_O250I = []
    for _ in range(90):
        new_acc = accounts.add()
        _addresses_O250I.append(new_acc)
        #get random 91 O50 token amounts and random 90 O250 token amounts
    _tokens_O50I = []
    for _ in range(90):
        _tokens_O50I.append(randint(1*10**16, 10*10**16))

    _tokens_O250I = []
    for _ in range(90):
        _tokens_O250I.append(randint(1*10**16, 10*10**16))

    assert len( _addresses_O50I) + len( _addresses_O250I) == 180
    assert len( _tokens_O50I) + len( _tokens_O250I) == 180
   
    vesting.newMulInvestors(_addresses_O50I,
                                        _addresses_O250I,
                                        _tokens_O50I, 
                                        _tokens_O250I,
                                        _timeLock_O250I,
                                        {"from":legacy_network})
    
        
   