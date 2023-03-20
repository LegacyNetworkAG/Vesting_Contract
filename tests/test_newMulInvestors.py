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
    Alice = accounts[1]
    Bob = accounts[2]
    Carol = accounts[3]
    David = accounts[4] 
    Hacker = accounts[5] 

    _timeLock_O250I = 2592000 #1 month lock period

    # should revert because the contract doesn't have enough funds (needs 330 and only gets 1 in funding)
    tokenContract.transfer(vesting,
                            1*10**18,
                            {"from": legacy_network})
    
    _addresses_O50I = [Alice, Bob]
    _addresses_O250I = [Carol, David]
    _tokens_O50I = [10*10**18, 20*10**18]
    _tokens_O250I = [100*10**18, 200*10**18]
    with brownie.reverts():
        vesting.newMulInvestors(_addresses_O50I,
                                        _addresses_O250I,
                                        _tokens_O50I, 
                                        _tokens_O250I,
                                        _timeLock_O250I,
                                        {"from":legacy_network})
    
    # should revert because addresses and token amounts for O50 mismatch
    tokenContract.transfer(vesting,
                            329*10**18,
                            {"from": legacy_network})# contract has enough funds now
    
    _addresses_O50I = [Alice]
    _addresses_O250I = [Carol, David]
    _tokens_O50I = [10*10**18, 20*10**18]
    _tokens_O250I = [100*10**18, 200*10**18]
    with brownie.reverts(encode_custom_error('VestingContract', 'addressAmountMismatch', [1, 2])):
        vesting.newMulInvestors(_addresses_O50I,
                                        _addresses_O250I,
                                        _tokens_O50I, 
                                        _tokens_O250I,
                                        _timeLock_O250I,
                                        {"from":legacy_network})

    # should revert because addresses and token amounts for O250 mismatch
    _addresses_O50I = [Alice, Bob]
    _addresses_O250I = [Carol, David]
    _tokens_O50I = [10*10**18, 20*10**18]
    _tokens_O250I = [100*10**18]
    with brownie.reverts(encode_custom_error('VestingContract', 'addressAmountMismatch', [2, 1])):
        vesting.newMulInvestors(_addresses_O50I,
                                        _addresses_O250I,
                                        _tokens_O50I, 
                                        _tokens_O250I,
                                        _timeLock_O250I,
                                        {"from":legacy_network})

    # should revert because there are 2 equal users (Bob) in 050
    _addresses_O50I = [Alice, Bob, Bob]
    _addresses_O250I = [Carol, David]
    _tokens_O50I = [10*10**18, 10*10**18, 10*10**18]
    _tokens_O250I = [100*10**18, 200*10**18]
    with brownie.reverts(encode_custom_error('VestingContract', 'addressAlreadyVested', [Bob.address])):
        vesting.newMulInvestors(_addresses_O50I,
                                        _addresses_O250I,
                                        _tokens_O50I, 
                                        _tokens_O250I,
                                        _timeLock_O250I,
                                        {"from":legacy_network})
        
    # should revert because there are 2 equal users (Carol) in 0250
    _addresses_O50I = [Alice, Bob]
    _addresses_O250I = [Carol, David, Carol]
    _tokens_O50I = [10*10**18, 20*10**18]
    _tokens_O250I = [100*10**18, 100*10**18, 100*10**18]
    with brownie.reverts(encode_custom_error('VestingContract', 'addressAlreadyVested', [Carol.address])):
        vesting.newMulInvestors(_addresses_O50I,
                                        _addresses_O250I,
                                        _tokens_O50I, 
                                        _tokens_O250I,
                                        _timeLock_O250I,
                                        {"from":legacy_network})

    # should revert because there are 2 equal users (Alice) in between O50 and O250
    _addresses_O50I = [Alice, Bob]
    _addresses_O250I = [Carol, David, Alice]
    _tokens_O50I = [10*10**18, 20*10**18]
    _tokens_O250I = [100*10**18, 100*10**18, 100*10**18]
    with brownie.reverts(encode_custom_error('VestingContract', 'addressAlreadyVested', [Alice.address])):
        vesting.newMulInvestors(_addresses_O50I,
                                        _addresses_O250I,
                                        _tokens_O50I, 
                                        _tokens_O250I,
                                        _timeLock_O250I,
                                        {"from":legacy_network})
        
    # should revert because it is not the contract's owner who calls the function
    _addresses_O50I = [Alice, Bob]
    _addresses_O250I = [Carol, David]
    _tokens_O50I = [10*10**18, 20*10**18]
    _tokens_O250I = [100*10**18, 200*10**18]
    with brownie.reverts():
        vesting.newMulInvestors(_addresses_O50I,
                                        _addresses_O250I,
                                        _tokens_O50I, 
                                        _tokens_O250I,
                                        _timeLock_O250I,
                                        {"from":Hacker})
        
    # reverts because there are more than 180 addresses
        #get random 91 O50 addresses and random 90 O250 addresses
    _addresses_O50I = []
    for _ in range(91):
        new_acc = accounts.add()
        _addresses_O50I.append(new_acc)

    _addresses_O250I = []
    for _ in range(90):
        new_acc = accounts.add()
        _addresses_O250I.append(new_acc)
        #get random 91 O50 token amounts and random 90 O250 token amounts
    _tokens_O50I = []
    for _ in range(91):
        _tokens_O50I.append(randint(1*10**16, 10*10**16))

    _tokens_O250I = []
    for _ in range(90):
        _tokens_O250I.append(randint(1*10**16, 10*10**16))

    assert len( _addresses_O50I) + len( _addresses_O250I) == 181
    assert len( _tokens_O50I) + len( _tokens_O250I) == 181
    with brownie.reverts(encode_custom_error('VestingContract', 'inputTooLarge', [180, len( _addresses_O50I) + len( _addresses_O250I)])):
        vesting.newMulInvestors(_addresses_O50I,
                                        _addresses_O250I,
                                        _tokens_O50I, 
                                        _tokens_O250I,
                                        _timeLock_O250I,
                                        {"from":legacy_network})
    
    # reverts because the address is a zero address
    _addresses_O50I = [Alice, '0x0000000000000000000000000000000000000000']
    _addresses_O250I = [Carol, David]
    _tokens_O50I = [10*10**18, 20*10**18]
    _tokens_O250I = [100*10**18, 200*10**18]
    with brownie.reverts():
        vesting.newMulInvestors(_addresses_O50I,
                                        _addresses_O250I,
                                        _tokens_O50I, 
                                        _tokens_O250I,
                                        _timeLock_O250I,
                                        {"from":legacy_network})
        
    # reverts because the address is the contract's own address
    _addresses_O50I = [Alice, Bob]
    _addresses_O250I = [Carol, vesting]
    _tokens_O50I = [10*10**18, 20*10**18]
    _tokens_O250I = [100*10**18, 200*10**18]
    with brownie.reverts():
        vesting.newMulInvestors(_addresses_O50I,
                                        _addresses_O250I,
                                        _tokens_O50I, 
                                        _tokens_O250I,
                                        _timeLock_O250I,
                                        {"from":legacy_network})       
'''
Test regular scenarios for newMullInvestors
&
Test if it reverts if we try to add an existing vester address in a separate function call
'''
def test_regularNewMull(tokenContract, vesting):
    # fetch the account
    legacy_network = accounts[0]
    Alice = accounts[1]
    Bob = accounts[2]
    Carol = accounts[3]
    David = accounts[4]  
    Eric = accounts[5]
    Fernanda = accounts[6]

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
    

    # should revert if it tries to add an existing address as a new vester in a separate call
    #Fund contract
    tokenContract.transfer(vesting,
                            1*10**18,
                            {"from": legacy_network})
    _addresses_O50I = [Alice]
    _addresses_O250I = []
    _tokens_O50I = [1*10**18]
    _tokens_O250I = []
    _timeLock_O250I = 2592000 #1 month lock period
    with brownie.reverts():
        vesting.newMulInvestors(_addresses_O50I,
                                            _addresses_O250I,
                                            _tokens_O50I, 
                                            _tokens_O250I,
                                            _timeLock_O250I,
                                            {"from":legacy_network})
        
    # should revert if we tried to add more users without sending more tokens to the contract
    _addresses_O50I = [Eric]
    _addresses_O250I = [Fernanda]
    _tokens_O50I = [1*10**18]
    _tokens_O250I = [10*10**18]
    _timeLock_O250I = 2592000 #1 month lock period
    with brownie.reverts():
        vesting.newMulInvestors(_addresses_O50I,
                                            _addresses_O250I,
                                            _tokens_O50I, 
                                            _tokens_O250I,
                                            _timeLock_O250I,
                                            {"from":legacy_network})
    
    # should pass if we tried to add more users after sending more tokens to the contract
    #Fund contract
    tokenContract.transfer(vesting,
                            10*10**18,
                            {"from": legacy_network})
    _addresses_O50I = [Eric]
    _addresses_O250I = [Fernanda]
    _tokens_O50I = [1*10**18]
    _tokens_O250I = [10*10**18]
    _timeLock_O250I = 2592000 #1 month lock period

    vesting.newMulInvestors(_addresses_O50I,
                                            _addresses_O250I,
                                            _tokens_O50I, 
                                            _tokens_O250I,
                                            _timeLock_O250I,
                                            {"from":legacy_network})