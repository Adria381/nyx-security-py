# Integration with Other Services

This guide explains how to use nyx-security with various services and frameworks.

## Discord.py Integration

### Basic Token Management

```python
from nyx_security import TokenManager
import discord
from discord.ext import commands

# Initialize token manager
token_manager = TokenManager()

# Store the token (do this once, ideally in a setup script)
# token_manager.store_token("discord_bot", "your_bot_token_here")

# Retrieve the token for use
bot_token = token_manager.retrieve_token("discord_bot")

# Create and run bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# Add your commands here

bot.run(bot_token)
```

### Advanced: Environment-Aware Token Management

```python
import os
from nyx_security import TokenManager, encrypt_data, decrypt_data

class SecureDiscordBot:
    def __init__(self):
        self.token_manager = TokenManager()
        self.env = os.getenv("ENV", "development")
        
    def initialize_token(self, token):
        """Store the token initially (run this once)"""
        # Store with environment-specific name
        self.token_manager.store_token(f"discord_bot_{self.env}", token)
        print(f"Token stored for {self.env} environment")
        
    def get_token(self):
        """Retrieve the token for the current environment"""
        try:
            return self.token_manager.retrieve_token(f"discord_bot_{self.env}")
        except ValueError:
            print(f"No token found for {self.env} environment")
            return None
            
    def run_bot(self):
        """Run the Discord bot with the secure token"""
        import discord
        from discord.ext import commands
        
        token = self.get_token()
        if not token:
            print("Cannot run bot: No token available")
            return
            
        bot = commands.Bot(command_prefix="!")
        
        @bot.event
        async def on_ready():
            print(f"Logged in as {bot.user} in {self.env} environment")
            
        # Add your commands here
            
        bot.run(token)
```

### Encrypting Sensitive User Data

If your Discord bot stores user data, you can use nyx-security to encrypt it:

```python
from nyx_security import encrypt_data, decrypt_data
import json

class UserDataManager:
    def __init__(self, master_password):
        self.master_password = master_password
        self.data_file = "user_data.json"
        
    def save_user_data(self, user_id, sensitive_data):
        """Encrypt and save user data"""
        # Load existing data
        try:
            with open(self.data_file, "r") as f:
                all_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            all_data = {}
            
        # Encrypt the user's data
        encrypted = encrypt_data(json.dumps(sensitive_data), self.master_password)
        
        # Store it
        all_data[str(user_id)] = encrypted
        
        # Save back to file
        with open(self.data_file, "w") as f:
            json.dump(all_data, f, indent=2)
            
    def get_user_data(self, user_id):
        """Retrieve and decrypt user data"""
        try:
            with open(self.data_file, "r") as f:
                all_data = json.load(f)
                
            if str(user_id) not in all_data:
                return None
                
            encrypted = all_data[str(user_id)]
            
            # Decrypt the data
            decrypted = decrypt_data(
                encrypted["encrypted_data"],
                self.master_password,
                encrypted["salt"],
                encrypted["iv"],
                encrypted["mac"]
            )
            
            return json.loads(decrypted)
            
        except Exception as e:
            print(f"Error retrieving user data: {e}")
            return None
```

### Complete Discord.py Bot Example

Here's a complete example of a Discord bot using nyx-security:

```python
import discord
from discord.ext import commands
import os
import json
from nyx_security import TokenManager, encrypt_data, decrypt_data

# Initialize security components
token_manager = TokenManager()
master_password = os.getenv("MASTER_PASSWORD", "change-this-in-production")

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# User data storage
user_data_file = "user_data.json"

def save_user_secret(user_id, secret_name, secret_value):
    """Save an encrypted secret for a user"""
    try:
        # Load existing data
        try:
            with open(user_data_file, "r") as f:
                all_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            all_data = {}
            
        # Initialize user data if needed
        if str(user_id) not in all_data:
            all_data[str(user_id)] = {}
            
        # Encrypt the secret
        encrypted = encrypt_data(secret_value, f"{master_password}{user_id}")
        
        # Store it
        all_data[str(user_id)][secret_name] = encrypted
        
        # Save back to file
        with open(user_data_file, "w") as f:
            json.dump(all_data, f, indent=2)
            
        return True
    except Exception as e:
        print(f"Error saving secret: {e}")
        return False

def get_user_secret(user_id, secret_name):
    """Retrieve and decrypt a user's secret"""
    try:
        # Load data
        with open(user_data_file, "r") as f:
            all_data = json.load(f)
            
        if str(user_id) not in all_data or secret_name not in all_data[str(user_id)]:
            return None
            
        encrypted = all_data[str(user_id)][secret_name]
        
        # Decrypt the secret
        decrypted = decrypt_data(
            encrypted["encrypted_data"],
            f"{master_password}{user_id}",
            encrypted["salt"],
            encrypted["iv"],
            encrypted["mac"]
        )
        
        return decrypted
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        return None

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def store(ctx, secret_name, *, secret_value):
    """Store an encrypted secret"""
    # Delete the user's message to prevent the secret from being visible
    await ctx.message.delete()
    
    if save_user_secret(ctx.author.id, secret_name, secret_value):
        await ctx.send(f"✅ Your secret '{secret_name}' has been securely stored.")
    else:
        await ctx.send("❌ There was an error storing your secret.")

@bot.command()
async def retrieve(ctx, secret_name):
    """Retrieve a stored secret"""
    # Send the secret as a DM for privacy
    secret = get_user_secret(ctx.author.id, secret_name)
    
    if secret:
        try:
            await ctx.author.send(f"🔒 Your secret '{secret_name}': {secret}")
            await ctx.send("✅ Secret sent to your DMs.")
        except discord.Forbidden:
            await ctx.send("❌ I couldn't send you a DM. Please enable DMs from server members.")
    else:
        await ctx.send(f"❓ No secret found with the name '{secret_name}'.")

@bot.command()
async def list_secrets(ctx):
    """List all secret names stored for the user"""
    try:
        with open(user_data_file, "r") as f:
            all_data = json.load(f)
            
        if str(ctx.author.id) not in all_data:
            await ctx.send("You don't have any secrets stored.")
            return
            
        secrets = list(all_data[str(ctx.author.id)].keys())
        await ctx.send(f"Your stored secrets: {', '.join(secrets)}")
    except (FileNotFoundError, json.JSONDecodeError):
        await ctx.send("You don't have any secrets stored.")

# Run the bot
bot.run(token_manager.retrieve_token("discord_bot"))
```

## Web Applications

nyx-security can be integrated with web frameworks like Flask or Django to enhance security:

```python
from flask import Flask, request, session
from nyx_security import encrypt_data, decrypt_data
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Master encryption password (in production, store this securely)
MASTER_PASSWORD = os.getenv("MASTER_PASSWORD", "change-this-in-production")

@app.route("/store", methods=["POST"])
def store_sensitive_data():
    """Store encrypted sensitive data in the session"""
    data = request.form.get("sensitive_data")
    if not data:
        return {"error": "No data provided"}, 400
        
    # Encrypt the data
    encrypted = encrypt_data(data, MASTER_PASSWORD)
    
    # Store in session
    session["encrypted_data"] = encrypted
    
    return {"status": "Data stored securely"}

@app.route("/retrieve", methods=["GET"])
def retrieve_sensitive_data():
    """Retrieve and decrypt data from the session"""
    if "encrypted_data" not in session:
        return {"error": "No data found"}, 404
        
    encrypted = session["encrypted_data"]
    
    try:
        # Decrypt the data
        decrypted = decrypt_data(
            encrypted["encrypted_data"],
            MASTER_PASSWORD,
            encrypted["salt"],
            encrypted["iv"],
            encrypted["mac"]
        )
        
        return {"data": decrypted}
    except Exception as e:
        return {"error": f"Decryption failed: {str(e)}"}, 500
```

## Database Connections

Secure your database connection strings:

```python
from nyx_security import TokenManager
import psycopg2
import sqlite3

# Initialize token manager
token_manager = TokenManager()

# Store database credentials (do this once)
token_manager.store_token("postgres_main", "postgresql://user:password@localhost:5432/mydb")
token_manager.store_token("sqlite_path", "/path/to/sensitive/database.sqlite")

# Later, when connecting to the database
def get_postgres_connection():
    """Get a PostgreSQL connection with securely stored credentials"""
    connection_string = token_manager.retrieve_token("postgres_main")
    return psycopg2.connect(connection_string)

def get_sqlite_connection():
    """Get a SQLite connection with securely stored path"""
    db_path = token_manager.retrieve_token("sqlite_path")
    return sqlite3.connect(db_path)
```

## API Clients

Secure API keys for third-party services:

```python
from nyx_security import TokenManager
import requests

# Initialize token manager
token_manager = TokenManager()

# Store API keys (do this once)
token_manager.store_token("github_api", "ghp_yourgithubpersonalaccesstoken")
token_manager.store_token("openai_api", "sk-youropenaiapikeyhere")

# Use the API keys in your client code
def github_api_request(endpoint, method="GET", data=None):
    """Make a GitHub API request with the securely stored token"""
    api_key = token_manager.retrieve_token("github_api")
    
    headers = {
        "Authorization": f"token {api_key}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    url = f"https://api.github.com/{endpoint}"
    
    if method == "GET":
        response = requests.get(url, headers=headers)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=data)
    elif method == "PUT":
        response = requests.put(url, headers=headers, json=data)
    elif method == "DELETE":
        response = requests.delete(url, headers=headers)
    else:
        raise ValueError(f"Unsupported method: {method}")
        
    return response.json()

def openai_api_request(prompt, model="gpt-3.5-turbo"):
    """Make an OpenAI API request with the securely stored token"""
    api_key = token_manager.retrieve_token("openai_api")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=data
    )
    
    return response.json()
```