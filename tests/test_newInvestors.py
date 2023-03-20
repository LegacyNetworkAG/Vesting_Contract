from eth_utils.abi import function_abi_to_4byte_selector, collapse_if_tuple
from brownie import accounts, chain, mock_token, VestingContract
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

    # should revert because the contract lacks funds
    amount=100*10**18
    with brownie.reverts():
        vesting.newInvestor(amount,
                                timeLock,
                                Alice,
                                {"from":legacy_network})

    tokenContract.transfer(vesting,
                            100*10**18,
                            {"from": legacy_network})
    
    # should revert because it is not the contract's owner who calls the function
    amount=100*10**18
    with brownie.reverts():
        vesting.newInvestor(amount,
                                timeLock,
                                Alice,
                                {"from":Hacker})
        
'''
Test regular scenarios for newInvestors
&
Test if it reverts if we try to add an existing vester address in a separate function call
'''
def test_regularNewInv(tokenContract, vesting):
    # Accounts
    legacy_network = accounts[0]
    Alice = accounts[1]
    Bob = accounts[2]


    # Variables
    amount=100*10**18
    timeLock = 2592000 #1 month lock period

    # Fund contract
    tokenContract.transfer(vesting,
                            200*10**18,
                            {"from": legacy_network})

    # should pass
    tokenContract.approve(vesting, amount, {"from": legacy_network})
    vesting.newInvestor(amount,
                                timeLock,
                                Alice,
                                {"from":legacy_network})
    tokenContract.approve(vesting, amount, {"from": legacy_network})
    vesting.newInvestor(amount,
                                timeLock,
                                Bob,
                                {"from":legacy_network})

    # Fund contract
    tokenContract.transfer(vesting,
                            200*10**18,
                            {"from": legacy_network})
    
    # should revert because the new investor is already vested
    print('---------------\n',encode_custom_error('VestingContract', 'addressAlreadyVested', [Alice.address]))
    with brownie.reverts(encode_custom_error('VestingContract', 'addressAlreadyVested', [Alice.address])):
        vesting.newInvestor(amount,
                                timeLock,
                                Alice,
                                {"from":legacy_network})
        
    # should release all funds to Alice
    secondsInMonth = 2592000 
    assert tokenContract.balanceOf(Alice, {'from': Alice}) ==  0
    chain.mine(timedelta=secondsInMonth*7)# time passed since vesting = 7 months
    vesting.release({"from": Alice})
    assert tokenContract.balanceOf(Alice, {'from': Alice}) ==  amount