import os
import fastapi
import bittensor as bt
import uvicorn
import subprocess
from typing import Dict, Tuple
from fastapi import Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from dotenv import load_dotenv

from app.auth.auth import get_current_username
from app.constants import ROUND_TABLE_HOTKEY, NETWORK
from app.proxy.proxy import Proxy

app = fastapi.FastAPI()

# Set up templates
templates = Jinja2Templates(directory="templates")

load_dotenv()

wallet_names = ["black", "white"]
delegators = ["5F5WLLEzDBXQDdTzDYgbQ3d3JKbM15HhPdFuLMmuzcUW5xG2", "5F99Qc6hZ67Jd6fW9jXgD3h9Jg4K5pQ9jXgD3h9Jg4K5p"]
wallets: Dict[str, Tuple[bt.wallet, str]] = {}
proxy = Proxy(NETWORK)

def unlock_wallets():
    for wallet_name in wallet_names:
        wallet = bt.wallet(name=wallet_name)
        print(f"Unlocking wallet {wallet_name}")
        retries = 3
        for _ in range(retries):
            try:
                wallet.unlock_coldkey()
                break
            except Exception as e:
                print(f"Error unlocking wallet {wallet_name}: {e}")
                continue
        wallets[wallet_name] = (wallet, delegators[wallet_names.index(wallet_name)])

@app.get("/")
def read_root(request: fastapi.Request, username: str = Depends(get_current_username)):
    subtensor = bt.subtensor(network=NETWORK)
    def get_balance_html():
        balance_html = ""
        for wallet_name in wallet_names:
            wallet, _ = wallets[wallet_name]
            balance = subtensor.get_balance(wallet.coldkey.ss58_address)
            balance_html += f"""
                <div class="balance-container">
                    <div class="balance-title"><a target="_blank" href="/stake_list?wallet_name={wallet_name}" style="text-decoration: none; color: inherit; cursor: pointer; text-decoration: underline;">{wallet_name}</a></div>
                    <div class="balance-amount">{balance} TAO</div>
                </div>
            """
        return balance_html

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "balance_html": get_balance_html(), "wallet_names": wallet_names}
    )


@app.get("/min_tolerance")
def min_tolerance(
    tao_amount: float, 
    netuid: int, 
):
    subtensor = bt.subtensor(network=NETWORK)
    subnet = subtensor.subnet(netuid=netuid)
    min_tolerance = tao_amount / subnet.tao_in.tao  
    return {"min_tolerance": min_tolerance}


@app.get("/stake")
def stake(
    tao_amount: float, 
    netuid: int, 
    wallet_name: str, 
    dest_hotkey: str = ROUND_TABLE_HOTKEY, 
    rate_tolerance: float = 0.005,
    min_tolerance_staking: bool = True,
    retries: int = 1,
    username: str = Depends(get_current_username)
):
    if retries < 1:
        retries = 1
    result = None
    min_tolerance = None
    wallet, delegator = wallets[wallet_name]
    subtensor = bt.subtensor(network=NETWORK)
    subnet = subtensor.subnet(netuid=netuid)
    min_tolerance = tao_amount / subnet.tao_in.tao  
    if min_tolerance_staking:
        rate_tolerance = min_tolerance + 0.001

    while retries > 0:
        try:
            result = proxy.add_stake(
                amount= bt.Balance.from_tao(tao_amount),
                proxy_wallet=wallet,
                delegator=delegator,
                netuid=netuid,
                hotkey=dest_hotkey,
                tolerance=rate_tolerance,
            )
            if not result:
                raise Exception("Stake failed")
            
            return {
                "success": True,
                "result": result,
                "min_tolerance": min_tolerance,
            }
        except Exception as e:
            retries -= 1
            if retries == 0:
                return {
                    "success": False,
                    "result": result,
                    "min_tolerance": min_tolerance,
                }


@app.get("/unstake")
def unstake(
    netuid: int,
    wallet_name: str,
    amount: float = None,
    dest_hotkey: str = ROUND_TABLE_HOTKEY,
    rate_tolerance: float = 0.005,
    min_tolerance_unstaking: bool = True,
    retries: int = 1,
    username: str = Depends(get_current_username)
):
    if retries < 1:
        retries = 1
    result = None
    wallet, delegator = wallets[wallet_name]
    subtensor = bt.subtensor(network=NETWORK)
    subnet = subtensor.subnet(netuid=netuid)

    if amount is None:
        amount = subtensor.get_stake(
            coldkey_ss58=wallet.coldkeypub.ss58_address,
            hotkey_ss58=dest_hotkey,
            netuid=netuid
        )
    else:
        amount = bt.Balance.from_tao(amount / subnet.price.tao, netuid)
                    
    min_tolerance = amount.tao / (amount.tao + subnet.alpha_in.tao)

    if min_tolerance_unstaking:
        rate_tolerance = min_tolerance + 0.001

    while retries > 0:
        try:
            result = proxy.remove_stake(
                netuid=netuid, 
                proxy_wallet=wallet, 
                delegator=delegator,
                amount=amount,
                hotkey=dest_hotkey,
                tolerance=rate_tolerance,
            )
            if not result:
                raise Exception("Unstake failed")
            
            return {
                "success": True,
                "result": result,
                "min_tolerance": min_tolerance,
            }
        
        except Exception as e:
            retries -= 1
            if retries == 0:
                return {
                    "success": False,
                    "result": result,
                    "min_tolerance": min_tolerance,
                }


@app.get("/stake_list")
def stake_list(wallet_name: str):
    result = subprocess.run(["btcli", "stake", "list", "--name", wallet_name, "--no-prompt"], capture_output=True, text=True)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{wallet_name} | Stake List</title>
    </head>
    <body>
        <pre>{result.stdout}</pre>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    unlock_wallets()
    if not wallet_names:
        print("No wallet names found in .env file")
        exit(1)
    uvicorn.run(app, host="0.0.0.0", port=9000)