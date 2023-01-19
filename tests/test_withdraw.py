import pytest
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
def vestingContract(tokenContract):

    # fetch the account
    legacy_network = accounts[0]
    Alice = accounts[1]
    Bob = accounts[2]
    Carol = accounts[3]
    David = accounts[4]

    _addresses_O50I = [Alice, Bob]
    _addresses_O250I = [Carol, David]
    _tokens_O50I = [10*10**18, 20*10**18]
    _tokens_O250I = [100*10**18, 200*10**18]
    _percent_per_milestone = [2000, 4000, 4000]
    _timeLock_O250I = 2592000 #1 month lock period
    _tokenAddress = tokenContract
    # deploy Staking contract
    vesting = VestingContract.deploy(_addresses_O50I,
                                        _addresses_O250I,
                                        _tokens_O50I, 
                                        _tokens_O250I,
                                        _percent_per_milestone,
                                        _timeLock_O250I,
                                        _tokenAddress,
                                        {"from":legacy_network})
    # print contract address
    print(f"Vesting contract deployed at {vesting}")
    return vesting

@pytest.fixture
def fundContract(tokenContract, vestingContract):
    # fetch the account
    legacy_network = accounts[0]

    #Fund contract
    transfer_token = tokenContract.transfer(vestingContract,
                                            330*10**18,
                                            {"from": legacy_network})
    print("Contract has been funded!")


'''
Test the revert
'''
#Test withdraw
def test_revert(tokenContract, vestingContract, fundContract):
    
    # fetch the accounts
    legacy_network = accounts[0]
    Alice = accounts[1]
    Bob = accounts[2]
    Carol = accounts[3]
    David = accounts[4]
    #Simulate passage of time (10 seconds)
    chain.mine(timedelta=10)
    Carol_balance_one = tokenContract.balanceOf(Carol ,{"from": Carol})
    vestingContract.release({"from": Alice})
    vestingContract.release({"from": Carol})

    assert tokenContract.balanceOf(Carol, {"from": Carol}) == Carol_balance_one   

'''
Test the release function, checking if 
        - the user balance is updated the correct amount
'''
def test_withdraw(tokenContract, vestingContract, fundContract):
    
    # fetch the accounts
    legacy_network = accounts[0]

    Alice = accounts[1]

    Carol = accounts[3]

    reward_ps_Alice = [0.2*10*10**18/2592000, 0.4*10*10**18/2592000, 0.4*10*10**18/2592000]
    reward_ps_Carol = [0.2*100*10**18/2592000, 0.4*100*10**18/2592000, 0.4*100*10**18/2592000]

    #Begin test
    Alice_balance_one = tokenContract.balanceOf(Alice ,{"from": Alice})
    Carol_balance_one = tokenContract.balanceOf(Carol ,{"from": Carol})

    assert tokenContract.balanceOf(Alice, {"from": Alice}) == Alice_balance_one 
    assert tokenContract.balanceOf(Carol, {"from": Carol}) == Carol_balance_one

    #Simulate passage of time (1 month)
    chain.mine(timedelta=2592000)

    vestingContract.release({"from": Alice})

    vestingContract.release({"from": Carol})
    print('1 month')
    print('Balance Alice=', tokenContract.balanceOf(Alice, {"from": Alice}))
    print('Theoretical Alice Balance', 2*10**18)
    print('Alice rewards per second (possible error)', reward_ps_Alice[1])
    print('Balance Carol=', tokenContract.balanceOf(Carol, {"from": Carol}))
    print('Theoretical Carol Balance', 0)
    print('Carol rewards per second (possible error)',reward_ps_Carol[0])
    assert abs(tokenContract.balanceOf(Alice, {"from": Alice}) - (Alice_balance_one + 0.2*10*10**18)) <= 5*reward_ps_Alice[0]
    assert abs(tokenContract.balanceOf(Carol, {"from": Carol}) - Carol_balance_one) <= 5*reward_ps_Carol[0]

    #Simulate passage of time (15 days)
    chain.mine(timedelta=2592000/2)

    vestingContract.release({"from": Alice})

    vestingContract.release({"from": Carol})

    print('1.5 months')
    print('Balance Alice=', tokenContract.balanceOf(Alice, {"from": Alice}))
    print('Theoretical Alice Balance', 2*10**18+(2592000/2)*reward_ps_Alice[1])
    print('Alice rewards per second (possible error)', reward_ps_Alice[1])
    print('Balance Carol=', tokenContract.balanceOf(Carol, {"from": Carol}))
    print('Theoretical Carol Balance', (2592000/2)*reward_ps_Carol[0])
    print('Carol rewards per second (possible error)',reward_ps_Carol[0])
    assert abs(tokenContract.balanceOf(Alice, {"from": Alice}) - (Alice_balance_one + 2*10**18+(2592000/2)*reward_ps_Alice[1])) <= 5*reward_ps_Alice[1]
    assert abs(tokenContract.balanceOf(Carol, {"from": Carol}) - (Carol_balance_one + (2592000/2)*reward_ps_Carol[0])) <= 5*reward_ps_Carol[0]


    #Simulate passage of time (2,5 months, so total time since deploying = 1m+0.5m+2.5m =4m => Both vestings are done)
    chain.mine(timedelta=2*2592000+2592000/2 +10)

    vestingContract.release({"from": Alice})

    vestingContract.release({"from": Carol})

    print('4 months')
    print('Balance Alice=', tokenContract.balanceOf(Alice, {"from": Alice}))
    print('Theoretical Alice Balance', 10*10**18)
    print('Alice rewards per second (possible error)', reward_ps_Alice[2])
    print('Balance Carol=', tokenContract.balanceOf(Carol, {"from": Carol}))
    print('Theoretical Carol Balance', 100*10**18)
    print('Carol rewards per second (possible error)',reward_ps_Carol[2])
    assert abs(tokenContract.balanceOf(Alice, {"from": Alice}) - (Alice_balance_one + 10*10**18)) <= 5*reward_ps_Alice[2]
    assert abs(tokenContract.balanceOf(Carol, {"from": Carol}) - (Carol_balance_one + 100*10**18)) <= 5*reward_ps_Carol[2]


'''
Test the revert in the new account 
'''
def test_newInvestorRevert(tokenContract, vestingContract, fundContract):
    # fetch the accounts
    legacy_network = accounts[0]

    John = accounts[5]
    Kate = accounts[6]

    vestingContract.new_Investor(10*10**18,John, 0, {"from": John})

'''
Test the new investor function 
'''
def test_newInvestor(tokenContract, vestingContract, fundContract):
    # fetch the accounts
    legacy_network = accounts[0]

    Alice = accounts[5]
    Carol = accounts[6]

    tokenContract.approve(vestingContract, 30*10**18, {"from": legacy_network})
    vestingContract.new_Investor(10*10**18,Alice, 0, {"from": legacy_network})
    vestingContract.new_Investor(20*10**18, Carol, 24*60*60, {"from": legacy_network})

    reward_ps_Alice = [0.2*10*10**18/2592000, 0.4*10*10**18/2592000, 0.4*10*10**18/2592000]
    reward_ps_Carol = [0.2*20*10**18/2592000, 0.4*20*10**18/2592000, 0.4*20*10**18/2592000]

    #Begin test
    Alice_balance_one = tokenContract.balanceOf(Alice ,{"from": Alice})
    Carol_balance_one = tokenContract.balanceOf(Carol ,{"from": Carol})

    assert tokenContract.balanceOf(Alice, {"from": Alice}) == Alice_balance_one 
    assert tokenContract.balanceOf(Carol, {"from": Carol}) == Carol_balance_one

    #Simulate passage of time (1 month)
    chain.mine(timedelta=2592000)

    vestingContract.release({"from": Alice})

    vestingContract.release({"from": Carol})
    print('1 month')
    print('Balance Alice=', tokenContract.balanceOf(Alice, {"from": Alice}))
    print('Theoretical Alice Balance', 2*10**18)
    print('Alice rewards per second (possible error)', reward_ps_Alice[1])
    print('Balance Carol=', tokenContract.balanceOf(Carol, {"from": Carol}))
    print('Theoretical Carol Balance', (2592000-24*60*60)*reward_ps_Carol[0])
    print('Carol rewards per second (possible error)',reward_ps_Carol[0])
    assert abs(tokenContract.balanceOf(Alice, {"from": Alice}) -  0.2*10*10**18) <= 2*reward_ps_Alice[1]
    assert abs(tokenContract.balanceOf(Carol, {"from": Carol}) - (2592000-24*60*60)*reward_ps_Carol[0]) <= 2*reward_ps_Carol[0]

    