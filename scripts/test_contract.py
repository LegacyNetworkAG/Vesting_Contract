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
    get_funds = connector.call(
            caller=_wallet_address,
            contract=_lock_contract,
            func_name="view_can_release_percent",
            func_params=[],
            to=_lockcontract_address,
    )
    print(get_funds['decoded']['0'])
#   print("Contract after withdrawn")
#     wallet_balance(connector, 
#                    _contract_Token, Token_contract_address, 
#                    investor, "Wallet three")

#
# Initialise
#    
def main():

    #Import Wallets
    (_wallet, _wallet_address) = wallet_import_mnemonic(1)
    (_wallet2, _wallet2_address) = wallet_import_mnemonic(2)

    #Connect to node
    connector = connect(1)

    _contract_Token = Contract.fromFile("Token_Mockup/build/contracts/mock_token.json")
    Token_contract_address='0x0828ebd4c6edd086d9496e3411202b7f3160ead3'
    _lock_contract = Contract.fromFile("build\contracts\LockContract.json")
    _lockcontract_address='0x74c02bd00679dfe7a3e36616d4b9dbc67d14c373'
    
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

investor = _wallet_address

test_withdraw(_wallet, _wallet_address, connector, _contract_Token,
                 Token_contract_address, _lock_contract, _lockcontract_address, investor)

withdraw_time = int(time.time())
lock_time=int(config('time_deployed'))
print(format((withdraw_time-lock_time) * 500*50000*(10**18)/10000/2592000, 'f'))
