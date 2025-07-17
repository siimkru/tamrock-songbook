# generate_token.py
import os
from google_auth_oauthlib.flow import InstalledAppFlow

# The scopes define what permissions the script is asking for.
# For this use case, 'drive.file' is sufficient as it allows creating files.
SCOPES = ['https://www.googleapis.com/auth/drive.file']
CLIENT_SECRETS_FILE = 'client_secret.json' # The file you downloaded

# Check if the client secrets file exists
if not os.path.exists(CLIENT_SECRETS_FILE):
    print(f"Error: The file '{CLIENT_SECRETS_FILE}' was not found.")
    print("Please download your OAuth 2.0 client credentials from the Google Cloud Console and place it in the same directory as this script.")
    exit()

# Create the flow instance
flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)

# Run the authorization flow. This will open a web browser.
print("Your browser will now open to ask for your permission.")
print("Please log in with your Google account and grant access.")
creds = flow.run_local_server(port=0)

# The flow is complete. The 'creds' object now contains your refresh token.
print("\n" + "="*50)
print("Authorization complete!")
print("="*50)
print(f"Your Client ID is: {creds.client_id}")
print(f"Your Client Secret is: {creds.client_secret}")
print("\nCOPY THIS REFRESH TOKEN and save it securely:")
print("="*50)
print(f"Your Refresh Token is: {creds.refresh_token}")
print("="*50)
print("\nYou will need to add these three values as secrets in your GitHub repository.")