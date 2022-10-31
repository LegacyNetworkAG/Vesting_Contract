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
    addresses_O50I = ['0x5959D60345aB12befE24bd8d21EF53eBa7688f6D',
                      '0x306A430F0E361e96E69D650067Eba3F73307b5C4'] # my wallets
    addresses_O250I = [] #saynode
    tokens_U50I=[50000*10**(18),
                1*10**(18)]
    tokens_O250I=[]
    percent_per_milestone=[5, 10, 15]#5%/100*10000
    percent_per_milestone = (percent_per_milestone)
    tokens_U50ITotal = sum(tokens_U50I)
    tokens_O250ITotal = sum(tokens_O250I)
    tokenAdress = "0x0828ebd4c6edd086d9496e3411202b7f3160ead3"

    #Deploy
    _lock_contract = Contract.fromFile("build\contracts\LockContract.json")
    res_lock_contract=connector.deploy(_wallet, _lock_contract, 
                                        ['address[]','address[]',
                                        'uint256[]', 'uint256[]','uint256[]',
                                        'uint256','uint256',
                                        'address'],
                                        [addresses_O50I, addresses_O250I,
                                        tokens_U50I, tokens_O250I, percent_per_milestone,
                                        tokens_U50ITotal, tokens_O250ITotal,
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
# Save the time in which the contract was deployed aka when the lock begins
dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)
os.environ["time_deployed"] = str(int(time.time()))
dotenv.set_key(dotenv_file, "time_deployed", os.environ["time_deployed"])
print(int(time.time()))
