from thor_requests.contract import Contract
from basic import connect, wallet_import_mnemonic
from decouple import config
import dotenv
import os
import time

#
# Deploy the lock contract
#
def deploy_lock_contract(connector, _wallet,_wallet_address, _wallet2_address):

    print("Deploy Lock Contract")

    #Constructor variables
    addresses_U50I = ['']
    addresses_O250I = ['']
    tokens_U50I=[1*10**(18),
                1*10**(18),
                1*10**(18)]
    tokens_O250I=[1*10**(18),
                1*10**(18),
                1*10**(18)]
    percent_per_milestone=[]
    initLock = 1224235235235
    tokens_U50ITotal = tokens_U50I.sum()
    tokens_O250ITotal = tokens_O250I.sum()
    tokenAdress = "0xee257dA9686d1531c6b8d18E053D4701c6F1e554"

    #Deploy
    _lock_contract = Contract.fromFile("build\contracts\LockContract.json")
    res_lock_contract=connector.deploy(_wallet, _lock_contract, 
                                        ['address[]','address[]',
                                        'uint256[]', 'uint256[]','uint8[]',
                                        'uint256','uint256','uint256',
                                        'address'],
                                        [addresses_U50I, addresses_O250I,
                                        tokens_U50I, tokens_O250I, percent_per_milestone,
                                        initLock, tokens_U50ITotal, tokens_O250ITotal,
                                        tokenAdress
                                        ])
    time.sleep(15)
    _lockcontract_address=connector.get_tx_receipt(res_lock_contract['id'])['outputs'][0]['contractAddress']

    # Set the value _lockcontract_address variable
    dotenv_file = dotenv.find_dotenv()
    dotenv.load_dotenv(dotenv_file)
    os.environ["_lockcontract_address"] = _lockcontract_address
    dotenv.set_key(dotenv_file, "_lockcontract_address", os.environ["_lockcontract_address"])

    print("TimeLock contract has been deployed in the address: " + str(_lockcontract_address)+"\n")


def main():

    #Import Wallets
    (_wallet, _wallet_address) = wallet_import_mnemonic(1)
    (_wallet2, _wallet2_address) = wallet_import_mnemonic(2)

    #Connect to node
    connector = connect(1)
    deploy_lock_contract(connector, _wallet,_wallet_address, _wallet2_address)
main()
