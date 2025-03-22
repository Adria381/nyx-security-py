"""
Command-line interface for nyx-security
"""

import argparse
import getpass
import json
import sys
from .token_manager import TokenManager
from .encryption import encrypt_data, decrypt_data


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="nyx-security - Token management and encryption")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Token commands
    token_parser = subparsers.add_parser("token", help="Token management")
    token_subparsers = token_parser.add_subparsers(dest="token_command", help="Token command")
    
    # Split token
    split_parser = token_subparsers.add_parser("split", help="Split a token")
    split_parser.add_argument("name", help="Name for the token")
    split_parser.add_argument("--parts", type=int, default=3, help="Number of parts to split into (default: 3)")
    split_parser.add_argument("--token", help="Token to split (if not provided, will prompt)")
    
    # List tokens
    token_subparsers.add_parser("list", help="List stored tokens")
    
    # Retrieve token
    retrieve_parser = token_subparsers.add_parser("retrieve", help="Retrieve a token")
    retrieve_parser.add_argument("name", help="Name of the token to retrieve")
    
    # Delete token
    delete_parser = token_subparsers.add_parser("delete", help="Delete a token")
    delete_parser.add_argument("name", help="Name of the token to delete")
    
    # Encryption commands
    encrypt_parser = subparsers.add_parser("encrypt", help="Encrypt data")
    encrypt_parser.add_argument("--data", help="Data to encrypt (if not provided, will prompt)")
    encrypt_parser.add_argument("--password", help="Password for encryption (if not provided, will prompt)")
    encrypt_parser.add_argument("--output", help="Output file (if not provided, prints to stdout)")
    
    decrypt_parser = subparsers.add_parser("decrypt", help="Decrypt data")
    decrypt_parser.add_argument("--input", help="Input file containing encrypted data and metadata")
    decrypt_parser.add_argument("--password", help="Password for decryption (if not provided, will prompt)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "token":
        handle_token_commands(args)
    elif args.command == "encrypt":
        handle_encrypt(args)
    elif args.command == "decrypt":
        handle_decrypt(args)


def handle_token_commands(args):
    """Handle token-related commands"""
    token_manager = TokenManager()
    
    if not args.token_command:
        print("Error: Token command is required")
        return
    
    if args.token_command == "split":
        token = args.token
        if not token:
            token = getpass.getpass("Enter token to split: ")
        
        parts = token_manager.store_token(args.name, token, args.parts)
        print(f"Token '{args.name}' split into {len(parts)} parts and stored.")
        print("Token parts:")
        for part in parts:
            print(f"  {part}")
    
    elif args.token_command == "list":
        tokens = token_manager.list_tokens()
        if tokens:
            print("Stored tokens:")
            for token in tokens:
                print(f"  {token}")
        else:
            print("No tokens stored.")
    
    elif args.token_command == "retrieve":
        try:
            token = token_manager.retrieve_token(args.name)
            print(f"Retrieved token '{args.name}':")
            print(token)
        except ValueError as e:
            print(f"Error: {e}")
    
    elif args.token_command == "delete":
        if token_manager.delete_token(args.name):
            print(f"Token '{args.name}' deleted.")
        else:
            print(f"Token '{args.name}' not found.")


def handle_encrypt(args):
    """Handle encryption command"""
    data = args.data
    if not data:
        data = input("Enter data to encrypt: ")
    
    password = args.password
    if not password:
        password = getpass.getpass("Enter encryption password: ")
    
    result = encrypt_data(data, password)
    
    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Encrypted data saved to {args.output}")
    else:
        print("Encrypted data:")
        for key, value in result.items():
            print(f"  {key}: {value}")


def handle_decrypt(args):
    """Handle decryption command"""
    if args.input:
        with open(args.input, "r") as f:
            data = json.load(f)
        
        encrypted_data = data["encrypted_data"]
        salt = data["salt"]
        iv = data["iv"]
        mac = data["mac"]
    else:
        print("Error: Input file is required for decryption")
        return
    
    password = args.password
    if not password:
        password = getpass.getpass("Enter decryption password: ")
    
    try:
        decrypted = decrypt_data(encrypted_data, password, salt, iv, mac)
        print("Decrypted data:")
        print(decrypted)
    except Exception as e:
        print(f"Error decrypting data: {e}")


if __name__ == "__main__":
    main()