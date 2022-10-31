import time
from thor_requests.contract import Contract
from basic import connect, wallet_import_mnemonic

def main():
        connector = connect(1)
        (_wallet, _wallet_address) = wallet_import_mnemonic(1)

        _contract_Token = Contract.fromFile('build\contracts\mock_token.json')

# 
# Get wallet balances, we use "call" in order to not waste any gas 
#
def wallet_balance(connector, 
                    _contract_Token, Token_contract_address, 
                    _wallet_address, name):

        balance_one = connector.call(
            caller=_wallet_address, # fill in your caller address or all zero address
            contract=_contract_Token,
            func_name="balanceOf",
            func_params=[_wallet_address],
            to=Token_contract_address,
        )
        print(name+" ("+str(_wallet_address)+") balance is: " + str(balance_one["decoded"]["0"]))
        return int(balance_one["decoded"]["0"])

#
#Wrap Token into wToken
#
def fund_contract(connector,
                _wallet,
                _contract_Token, Token_contract_address,
                _lockcontract_address,
                amount
                ):

        #
        send_Token = connector.transact(
            _wallet,
            contract=_contract_Token,
            func_name="transfer",
            func_params=[_lockcontract_address, amount],
            to=Token_contract_address,
        )
        time.sleep(15)

#
#Wrap Token into wToken
#
def send_token(connector,
                _wallet,
                _contract_Token, Token_contract_address,
                _wallet2_address,
                amount
                ):

        #
        send_Token = connector.transact(
            _wallet,
            contract=_contract_Token,
            func_name="transfer",
            func_params=[_wallet2_address, amount],
            to=Token_contract_address,
        )
        time.sleep(15)