from bcrypt import hashpw, gensalt
import getpass

def generate_hash(password: str) -> bytes:
    """
    Generate a bcrypt hash from a password.
    
    Args:
        password (str): The password to hash
        
    Returns:
        bytes: The hashed password
    """
    return hashpw(password.encode(), gensalt())

if __name__ == "__main__":
    # Get password from user input
    password = getpass.getpass("Enter password to hash: ")
    confirm_password = getpass.getpass("Confirm password: ")
    if password != confirm_password:
        print("Passwords do not match!")
        exit(1)
    hashed = generate_hash(password)
    print(f"Hashed: {hashed.decode()}")