import dotenv
import os
import time
from thor_requests.contract import Contract
from basic import connect, wallet_import_mnemonic
from decouple import config
# Deploy the Token contract
#     
def deploy_Token(connector, _wallet, _contract_Token):

        print("Deploy Token Contract")

        res_Token=connector.deploy(_wallet,  
                                    _contract_Token,
                                    [], 
                                    []
                                    )
        time.sleep(15)
        Token_contract_address=connector.get_tx_receipt(res_Token['id'])['outputs'][0]['contractAddress']

        print("Token contract has been deployed in the address: " + str(Token_contract_address)+"\n")

def main():
        connector = connect(1)
        (_wallet, _wallet_address) = wallet_import_mnemonic(1)

        _contract_Token = Contract.fromFile('build\contracts\mock_token.json')
        deploy_Token(connector, _wallet, _contract_Token)
main()