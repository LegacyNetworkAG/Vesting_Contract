from thor_requests.contract import Contract
from basic import connect, wallet_import_mnemonic
from decouple import config
import time


#   
# Get wallet balances, we use "call" in order to not waste any gas 
#
def wallet_balance(connector, _contract_Token, Token_contract_address, _address, name):

        balance_one = connector.call(
            caller=_wallet_address, # fill in your caller address or all zero address
            contract=_contract_Token,
            func_name="balanceOf",
            func_params=[_address],
            to=Token_contract_address,
        )
        print(name+" ("+str(_address)+") balance is: " + str(balance_one["decoded"]["0"]))
        return int(balance_one["decoded"]["0"])


#
# Test Withdraw
#
def test_withdraw(_wallet, _wallet_address, 
                  connector, 
                  _contract_Token, Token_contract_address,
                  _lock_contract, _lockcontract_address, 
                  investor):


    print("Start Withdraw test")

    print("Investor balance before withdraw")
    wallet_balance(connector, 
                   _contract_Token, Token_contract_address, 
                   investor, "Wallet three")

    #Attempts to withdrawe the "freed" tokens this investor is owned
    get_funds = connector.transact(
            _wallet,
            contract=_lock_contract,
            func_name="release",
            func_params=[],
            to=_lockcontract_address,
    )
    time.sleep(15)

    print("Contract after withdrawn")
    wallet_balance(connector, 
                   _contract_Token, Token_contract_address, 
                   investor, "Wallet three")

#
# Initialise
#    
def main():

    #Import Wallets
    (_wallet, _wallet_address) = wallet_import_mnemonic(1)
    (_wallet2, _wallet2_address) = wallet_import_mnemonic(2)

    #Connect to node
    connector = connect(1)

    _contract_Token = Contract.fromFile("build_static\LegacyToken.json")
    Token_contract_address=config('Token_contract_address')
    _lock_contract = Contract.fromFile("build\contracts\LockContract.json")
    _lockcontract_address=config('_lockcontract_address')
    
    return connector, \
           _wallet, _wallet_address, \
           _wallet2, _wallet2_address, \
           _contract_Token, Token_contract_address, \
           _lock_contract, _lockcontract_address




#
# Start Script
#
(connector, _wallet, _wallet_address, _wallet2, _wallet2_address , _contract_Token, 
Token_contract_address, _lock_contract, _lockcontract_address) = main()

investor = "0xee257dA9686d1531c6b8d18E053D4701c6F1e554"

test_withdraw(_wallet, _wallet_address, connector, _contract_Token,
                 Token_contract_address, _lock_contract, _lockcontract_address, investor)
