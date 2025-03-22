# nyx-security

A Python security module for token management and encryption, designed to enhance security in your applications without external dependencies.

## Features

- **Token Management**: Split sensitive tokens into multiple parts for enhanced security
- **Secure Storage**: Store and retrieve tokens securely
- **Encryption**: Encrypt and decrypt sensitive data using strong cryptographic methods
- **No External Dependencies**: Uses only Python's built-in libraries
- **Command-line Interface**: Easy-to-use CLI for all operations
- **Service Integration**: Easily integrate with Discord bots, web applications, and more

## Installation

```bash
pip install nyx-security
```

## Quick Start

### Token Management

```python
from nyx_security import TokenManager

# Create a token manager
manager = TokenManager()

# Split and store a token
api_token = "your-super-secret-api-token-here"
token_parts = manager.store_token("my_api_token", api_token)

# Later, retrieve the original token
original_token = manager.retrieve_token("my_api_token")
```

### Data Encryption

```python
from nyx_security import encrypt_data, decrypt_data

# Encrypt sensitive data
sensitive_data = "This is sensitive information that needs to be protected"
password = "secure-password-123"
encrypted = encrypt_data(sensitive_data, password)

# Later, decrypt the data
decrypted = decrypt_data(
    encrypted["encrypted_data"], 
    password, 
    encrypted["salt"], 
    encrypted["iv"], 
    encrypted["mac"]
)
```

## Command Line Usage

nyx-security provides a convenient command-line interface:

### Token Management

Split a token into parts:

```bash
nyx-security token split my_api_token
```

List stored tokens:

```bash
nyx-security token list
```

Retrieve a token:

```bash
nyx-security token retrieve my_api_token
```

### Encryption

Encrypt data:

```bash
nyx-security encrypt --data "sensitive information"
```

Decrypt data:

```bash
nyx-security decrypt --input encrypted_data.json
```

## How It Works

### Token Splitting

nyx-security uses a secure method to split tokens:

1. The original token is divided into multiple parts
2. Each part contains a portion of the original token
3. A unique identifier and salt are added to each part
4. The parts are stored securely

This approach ensures that:

- No single part contains the complete token
- The parts must be combined in the correct order
- Even if one part is compromised, the original token remains secure

### Encryption

The encryption system uses:

1. PBKDF2 with HMAC-SHA256 for key derivation
2. A secure XOR-based encryption with SHA-256 for the key stream
3. HMAC verification for data integrity
4. Unique salt and IV for each encryption operation

## Integration Examples

nyx-security can be integrated with various services:

### Discord.py

```python
from nyx_security import TokenManager
import discord
from discord.ext import commands

# Initialize token manager
token_manager = TokenManager()

# Retrieve the bot token
bot_token = token_manager.retrieve_token("discord_bot")

# Create and run the bot
bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

bot.run(bot_token)
```

See the [integrations documentation](docs/integrations.md) for more examples.

## Security Considerations

- The master password used for encryption should be stored securely
- For production use, consider using environment variables for sensitive values
- Token parts should be stored in separate locations for maximum security
- Regular rotation of tokens and passwords is recommended

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.