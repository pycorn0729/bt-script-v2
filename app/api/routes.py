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
    dest_hotkey: str = ROUND_TABLE_HOTKEY,
    rate_tolerance: float = 0.005,
    min_tolerance_staking: bool = True,
    retries: int = 1,
    username: str = Depends(get_current_username)
):
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
    dest_hotkey: str = ROUND_TABLE_HOTKEY,
    rate_tolerance: float = 0.005,
    min_tolerance_unstaking: bool = True,
    retries: int = 1,
    username: str = Depends(get_current_username)
):
    return stake_service.unstake(
        netuid=netuid,
        wallet_name=wallet_name,
        amount=amount,
        dest_hotkey=dest_hotkey,
        rate_tolerance=rate_tolerance,
        min_tolerance_unstaking=min_tolerance_unstaking,
        retries=retries
    )
