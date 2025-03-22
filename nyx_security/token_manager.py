"""
Token management utilities for nyx-security
"""

import os
import json
import secrets
from pathlib import Path
from typing import List, Tuple, Dict, Optional


def split_token(original_token: str, parts: int = 3) -> List[str]:
    """
    Split an original token into multiple parts.
    Each part contains information from the original token.
    
    Args:
        original_token: The token to split
        parts: Number of parts to split the token into (default: 3)
        
    Returns:
        List of token parts
    """
    if not original_token:
        raise ValueError("Original token cannot be empty")
    
    if parts < 2:
        raise ValueError("Token must be split into at least 2 parts")
    
    # Ensure the token is long enough to split
    min_length = parts * 2
    if len(original_token) < min_length:
        raise ValueError(f"Token must be at least {min_length} characters long to split into {parts} parts")
    
    # Calculate the base length for each part
    base_length = len(original_token) // parts
    remainder = len(original_token) % parts
    
    # Split the token
    token_parts = []
    start = 0
    
    for i in range(parts):
        # Add an extra character for the first 'remainder' parts
        part_length = base_length + (1 if i < remainder else 0)
        end = start + part_length
        
        # Extract the part and add a unique identifier
        part = original_token[start:end]
        # Add a unique salt to each part
        salt = secrets.token_hex(4)
        token_parts.append(f"{i+1}:{salt}:{part}")
        
        start = end
    
    return token_parts


def combine_tokens(token_parts: List[str]) -> str:
    """
    Combine token parts back into the original token.
    
    Args:
        token_parts: List of token parts created by split_token
        
    Returns:
        The original token
    """
    if not token_parts:
        raise ValueError("Token parts list cannot be empty")
    
    # Sort parts by their index
    sorted_parts = []
    for part in token_parts:
        try:
            index, salt, token_piece = part.split(":", 2)
            sorted_parts.append((int(index), token_piece))
        except (ValueError, IndexError):
            raise ValueError(f"Invalid token part format: {part}")
    
    # Sort by index and extract just the token pieces
    sorted_parts.sort(key=lambda x: x[0])
    token_pieces = [part[1] for part in sorted_parts]
    
    # Combine the pieces
    return "".join(token_pieces)


class TokenManager:
    """
    Manages token operations including splitting, storing, and retrieving tokens.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the TokenManager.
        
        Args:
            storage_path: Path to store token files (default: current directory)
        """
        self.storage_path = Path(storage_path) if storage_path else Path.cwd()
        self.tokens_file = self.storage_path / "tokens.json"
        
        # Create the storage directory if it doesn't exist
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Initialize the tokens file if it doesn't exist
        if not self.tokens_file.exists():
            with open(self.tokens_file, "w") as f:
                json.dump({}, f)
    
    def store_token(self, token_name: str, original_token: str, parts: int = 3) -> List[str]:
        """
        Split a token and store it.
        
        Args:
            token_name: Name to identify the token
            original_token: The token to split and store
            parts: Number of parts to split the token into
            
        Returns:
            List of token parts
        """
        # Split the token
        token_parts = split_token(original_token, parts)
        
        # Load existing tokens
        tokens = self._load_tokens()
        
        # Store the token parts
        tokens[token_name] = token_parts
        
        # Save the tokens
        self._save_tokens(tokens)
        
        return token_parts
    
    def retrieve_token(self, token_name: str) -> str:
        """
        Retrieve and combine a stored token.
        
        Args:
            token_name: Name of the token to retrieve
            
        Returns:
            The original token
        """
        # Load tokens
        tokens = self._load_tokens()
        
        # Check if the token exists
        if token_name not in tokens:
            raise ValueError(f"Token '{token_name}' not found")
        
        # Get the token parts
        token_parts = tokens[token_name]
        
        # Combine and return the token
        return combine_tokens(token_parts)
    
    def list_tokens(self) -> List[str]:
        """
        List all stored token names.
        
        Returns:
            List of token names
        """
        tokens = self._load_tokens()
        return list(tokens.keys())
    
    def delete_token(self, token_name: str) -> bool:
        """
        Delete a stored token.
        
        Args:
            token_name: Name of the token to delete
            
        Returns:
            True if the token was deleted, False if it didn't exist
        """
        tokens = self._load_tokens()
        
        if token_name not in tokens:
            return False
        
        del tokens[token_name]
        self._save_tokens(tokens)
        return True
    
    def _load_tokens(self) -> Dict[str, List[str]]:
        """Load tokens from the tokens file."""
        try:
            with open(self.tokens_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_tokens(self, tokens: Dict[str, List[str]]) -> None:
        """Save tokens to the tokens file."""
        with open(self.tokens_file, "w") as f:
            json.dump(tokens, f, indent=2)
