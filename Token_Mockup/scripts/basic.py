from traceback import print_tb
from thor_requests.connect import Connect
from thor_requests.wallet import Wallet
from decouple import config


# Import wallets from mnemonic (this should be only one, but for know we need 2 for testing)
def wallet_import_mnemonic(num):
    mne = 'MNEMONIC_' + str(num)
    MNEMONIC = config(mne)
    _wallet = Wallet.fromMnemonic(MNEMONIC.split(', '))
    _wallet_address = _wallet.getAddress()
    return _wallet, _wallet_address

#
# Connect to Veblocks and import the DHN contract
#
def connect(network_choice):

    if network_choice == 1:
        #Testnet node
        print("Connected to Veblocks Testnet Node\n")
        connector = Connect("https://testnet.veblocks.net")

    elif network_choice == 2:
        #Mainnet node
        print("Connected to Veblocks Mainnet Node")
        connector = Connect("http://3.124.193.149:8669")

    else:
        print("You must choose between 1 (Testnet) or 2 (Mainnet).")
    
    return connector