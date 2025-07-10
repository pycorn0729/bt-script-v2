import bittensor as bt
from typing import Dict, Tuple, Optional, Any

from app.constants import ROUND_TABLE_HOTKEY
from app.core.config import settings
from app.services.proxy import Proxy


class StakeService:
    """
    Service class for handling stake-related business logic.
    Encapsulates all staking operations including min tolerance calculations,
    stake/unstake operations with retry mechanisms, and error handling.
    """
    
    def __init__(self, wallets: Dict[str, Tuple[bt.wallet, str]]):
        """
        Initialize the StakeService with wallets and proxy instance.
        
        Args:
            wallets: Dictionary mapping wallet names to (wallet, delegator) tuples
            proxy: Proxy instance for handling stake operations
        """
        self.wallets = wallets
        self.proxy = Proxy(settings.NETWORK)
        self.subtensor = bt.subtensor(network=settings.NETWORK)
    
    def calculate_min_tolerance(self, tao_amount: float, netuid: int) -> float:
        """
        Calculate the minimum tolerance for staking operations.
        
        Args:
            tao_amount: Amount in TAO
            netuid: Network/subnet ID
            
        Returns:
            float: Minimum tolerance value
        """
        subnet = self.subtensor.subnet(netuid=netuid)
        if subnet is None:
            raise ValueError(f"Subnet with netuid {netuid} does not exist")
        min_tolerance = tao_amount / subnet.tao_in.tao
        return min_tolerance
    
    def stake(
        self,
        tao_amount: float,
        netuid: int,
        wallet_name: str,
        dest_hotkey: str = ROUND_TABLE_HOTKEY,
        rate_tolerance: float = 0.005,
        min_tolerance_staking: bool = True,
        retries: int = 1
    ) -> Dict[str, Any]:
        """
        Execute staking operation with retry mechanism and error handling.
        
        Args:
            tao_amount: Amount to stake in TAO
            netuid: Network/subnet ID
            wallet_name: Name of the wallet to use
            dest_hotkey: Destination hotkey address
            rate_tolerance: Tolerance for rate calculations
            min_tolerance_staking: Whether to use minimum tolerance
            retries: Number of retry attempts
            
        Returns:
            Dict containing success status, result, and min_tolerance
        """
        # Validate retries parameter
        if retries < 1:
            retries = 1
            
        result = None
        min_tolerance = None
        
        # Get wallet and delegator
        if wallet_name not in self.wallets:
            return {
                "success": False,
                "result": None,
                "min_tolerance": None,
                "error": f"Wallet '{wallet_name}' not found"
            }
            
        wallet, delegator = self.wallets[wallet_name]
        
        # Calculate minimum tolerance
        subnet = self.subtensor.subnet(netuid=netuid)
        if subnet is None:
            return {
                "success": False,
                "result": None,
                "min_tolerance": None,
                "error": f"Subnet with netuid {netuid} does not exist"
            }
        min_tolerance = tao_amount / subnet.tao_in.tao
        
        # Adjust rate tolerance if using minimum tolerance staking
        if min_tolerance_staking:
            rate_tolerance = min_tolerance + 0.001
        
        # Execute staking with retry mechanism
        while retries > 0:
            try:
                result, msg = self.proxy.add_stake(
                    amount=bt.Balance.from_tao(tao_amount),
                    proxy_wallet=wallet,
                    delegator=delegator,
                    netuid=netuid,
                    hotkey=dest_hotkey,
                    tolerance=rate_tolerance,
                )
                
                if not result:
                    raise Exception(f"Stake operation failed: {msg}")
                
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
                        "error": str(e)
                    }
        
        # This should never be reached, but required for type checking
        return {
            "success": False,
            "result": None,
            "min_tolerance": min_tolerance,
            "error": "Unexpected error in stake operation"
        }
    
    def unstake(
        self,
        netuid: int,
        wallet_name: str,
        amount: Optional[float] = None,
        dest_hotkey: str = ROUND_TABLE_HOTKEY,
        rate_tolerance: float = 0.005,
        min_tolerance_unstaking: bool = True,
        retries: int = 1
    ) -> Dict[str, Any]:
        """
        Execute unstaking operation with retry mechanism and error handling.
        
        Args:
            netuid: Network/subnet ID
            wallet_name: Name of the wallet to use
            amount: Amount to unstake (if None, unstakes all available)
            dest_hotkey: Destination hotkey address
            rate_tolerance: Tolerance for rate calculations
            min_tolerance_unstaking: Whether to use minimum tolerance
            retries: Number of retry attempts
            
        Returns:
            Dict containing success status, result, and min_tolerance
        """
        # Validate retries parameter
        if retries < 1:
            retries = 1
            
        result = None
        
        # Get wallet and delegator
        if wallet_name not in self.wallets:
            return {
                "success": False,
                "result": None,
                "min_tolerance": None,
                "error": f"Wallet '{wallet_name}' not found"
            }
            
        wallet, delegator = self.wallets[wallet_name]
        subnet = self.subtensor.subnet(netuid=netuid)
        
        if subnet is None:
            return {
                "success": False,
                "result": None,
                "min_tolerance": None,
                "error": f"Subnet with netuid {netuid} does not exist"
            }
        
        # Determine amount to unstake
        if amount is None:
            # Unstake all available balance
            amount_balance = self.subtensor.get_stake(
                coldkey_ss58=wallet.coldkeypub.ss58_address,
                hotkey_ss58=dest_hotkey,
                netuid=netuid
            )
        else:
            # Convert TAO amount to Balance object
            amount_balance = bt.Balance.from_tao(amount / subnet.price.tao, netuid)
        
        # Calculate minimum tolerance for unstaking
        min_tolerance = amount_balance.tao / (amount_balance.tao + subnet.alpha_in.tao)
        
        # Adjust rate tolerance if using minimum tolerance unstaking
        if min_tolerance_unstaking:
            rate_tolerance = min_tolerance + 0.001
        
        # Execute unstaking with retry mechanism
        while retries > 0:
            try:
                result, msg = self.proxy.remove_stake(
                    netuid=netuid,
                    proxy_wallet=wallet,
                    delegator=delegator,
                    amount=amount_balance,
                    hotkey=dest_hotkey,
                    tolerance=rate_tolerance,
                )
                
                if not result:
                    raise Exception(f"Unstake operation failed: {msg}")
                
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
                        "error": str(e)
                    }
        
        # This should never be reached, but required for type checking
        return {
            "success": False,
            "result": None,
            "min_tolerance": min_tolerance,
            "error": "Unexpected error in unstake operation"
        }
