import bittensor as bt
from typing import Optional
from fastapi import APIRouter, Depends
from app.constants import ROUND_TABLE_HOTKEY, NETWORK
from app.services.stake import StakeService
from app.services.auth import get_current_username
from app.services.wallets import wallets
from app.core.config import settings


router = APIRouter()

# Initialize the StakeService with wallets and proxy
stake_service = StakeService(wallets)


@router.get("/min_tolerance")
def min_tolerance(
    tao_amount: float,
    netuid: int,
):
    min_tol = stake_service.calculate_min_tolerance(tao_amount, netuid)
    return {"min_tolerance": min_tol}


@router.get("/stake")
def stake(
    tao_amount: float,
    netuid: int,
    wallet_name: str,
    dest_hotkey: str = settings.DEFAULT_DEST_HOTKEY,
    rate_tolerance: float = settings.DEFAULT_RATE_TOLERANCE,
    min_tolerance_staking: bool = settings.DEFAULT_MIN_TOLERANCE,
    retries: int = settings.DEFAULT_RETRIES,
    username: str = Depends(get_current_username)
):
    # Validate retries parameter
    if retries < 1:
        retries = 1    
    
    # Get wallet and delegator
    if wallet_name not in stake_service.wallets:
        return {
            "success": False,
            "error": f"Wallet '{wallet_name}' not found"
        }

    return stake_service.stake(
        tao_amount=tao_amount,
        netuid=netuid,
        wallet_name=wallet_name,
        dest_hotkey=dest_hotkey,
        rate_tolerance=rate_tolerance,
        min_tolerance_staking=min_tolerance_staking,
        retries=retries
    )


@router.get("/unstake")
def unstake(
    netuid: int,
    wallet_name: str,
    amount: Optional[float] = None,
    dest_hotkey: str = settings.DEFAULT_DEST_HOTKEY,
    rate_tolerance: float = settings.DEFAULT_RATE_TOLERANCE,
    min_tolerance_unstaking: bool = settings.DEFAULT_MIN_TOLERANCE,
    retries: int = settings.DEFAULT_RETRIES,
    username: str = Depends(get_current_username)
):
    # Validate retries parameter
    if retries < 1:
        retries = 1    
    
    # Get wallet and delegator
    if wallet_name not in stake_service.wallets:
        return {
            "success": False,
            "error": f"Wallet '{wallet_name}' not found"
        }

    return stake_service.unstake(
        netuid=netuid,
        wallet_name=wallet_name,
        amount=amount,
        dest_hotkey=dest_hotkey,
        rate_tolerance=rate_tolerance,
        min_tolerance_unstaking=min_tolerance_unstaking,
        retries=retries
    )
