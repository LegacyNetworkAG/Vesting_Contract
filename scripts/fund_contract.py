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
#Transfer Tokens to the contract
#
def trans_Token(connector,
                _wallet,
                _contract_Token, Token_contract_address,
                _lockcontract_address,
                amount
                ):

        #Transfer tokens to an address
        transf_Token = connector.transact(
            _wallet,
            contract=_contract_Token,
            func_name="transfer",
            func_params=[_lockcontract_address, amount],
            to=Token_contract_address,
        )
        time.sleep(15)

#
# Fund Contract
#
def fund_contract(_wallet, _wallet_address, connector, _contract_Token,
                  Token_contract_address, _lock_contract, _lockcontract_address):
                  
    trans_Token(connector,
                _wallet,
                _contract_Token, Token_contract_address,
                _lockcontract_address,
                50000*10**(18)
                )
    print("Token Balances")
    wallet_balance(connector, _contract_Token, Token_contract_address, _wallet_address, "Wallet's")
    wallet_balance(connector, _contract_Token, Token_contract_address, _lockcontract_address, "Contract's")
    
#
# Initialise
#    
def main():

    #Import Wallets
    (_wallet, _wallet_address) = wallet_import_mnemonic(1)

    #Connect to node
    connector = connect(1)

    _contract_Token = Contract.fromFile('build\contracts\mock_token.json')
    Token_contract_address='0x0828ebd4c6edd086d9496e3411202b7f3160ead3'
    _lock_contract = Contract.fromFile("build\contracts\LockContract.json")
    _lockcontract_address='0x312fd66225c3d9d0deb53c05826ec5de466608ea'
    
    return _wallet, _wallet_address, connector, _contract_Token, \
           Token_contract_address, _lock_contract, _lockcontract_address


#
# Start Script
#
(_wallet, _wallet_address, connector, _contract_Token, 
Token_contract_address, _lock_contract, _lockcontract_address) = main()
wallet_balance(connector, _contract_Token, Token_contract_address, _wallet_address, "Wallet's")
fund_contract(_wallet, _wallet_address, connector, _contract_Token,
                  Token_contract_address, _lock_contract, _lockcontract_address)