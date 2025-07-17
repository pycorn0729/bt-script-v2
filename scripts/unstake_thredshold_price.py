import sys
import os

# Add the parent directory to the Python search path (sys.path)
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
    
import bittensor as bt
from app.constants import NETWORK
from app.services.proxy import Proxy
from utils.logger import logger

if __name__ == '__main__':
    netuid = int(input("Enter the netuid: "))
    threshold = float(input("Enter the threshold: "))
    wallet_name = input("Enter the wallet name: ")
    delegator = input("Enter the delegator: ")
    dest_hotkey = input("Enter the dest hotkey: ")

    proxy = Proxy(network=NETWORK)
    proxy.init_runtime()
    subtensor = bt.subtensor(network=NETWORK)
    wallet = bt.wallet(name=wallet_name)
    wallet.unlock_coldkey()
    amount_balance = subtensor.get_stake(
        coldkey_ss58=delegator,
        hotkey_ss58=dest_hotkey,
        netuid=netuid
    )

    print("Press Ctrl+C to stop the script")
    print(f"Wallet: {wallet_name}, Delegator: {delegator}, Dest Hotkey: {dest_hotkey}, Amount: {amount_balance.tao}")

    while True:
        try:
            subnet = subtensor.subnet(netuid=netuid)
            if subnet is None:
                logger.error(f"Subnet is None for netuid: {netuid}")
                continue

            if amount_balance is None:
                logger.error(f"Amount balance is None for netuid: {netuid}")
                continue
            
            alpha_price = subnet.alpha_to_tao(1)
            logger.info(f"Current alpha token price: {alpha_price} TAO")
            
            if threshold != -1 and alpha_price < bt.Balance.from_tao(threshold):
                logger.info(f"Current price {alpha_price} TAO is below threshold {threshold} TAO. Skipping...")
                continue
            
            proxy.remove_stake(
                proxy_wallet=wallet,
                delegator=delegator,
                netuid=netuid,
                hotkey=dest_hotkey,
                amount=amount_balance,
                tolerance=0.005,
            )
            break
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
        