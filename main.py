import pandas as pd
from playwright.sync_api import sync_playwright
import time
import os
from platforms.twitter import TwitterBot
from platforms.webmail import WebmailBot

# Configuration
INPUT_FILE = "accounts_to_create.xlsx"
OUTPUT_FILE = "created_accounts_report.xlsx"

# ... imports ...
import re
from platforms import PLATFORM_MAP

# ... configuration ...

def get_platform_choice():
    print("\nAvailable Platforms:")
    platforms = sorted([p for p in PLATFORM_MAP.keys() if len(p) > 2])
    
    for i, p in enumerate(platforms):
        print(f"{i + 1}. {p}")
        
    choice = input("\nEnter the number of the platform to run (or 'all'): ")
    
    if choice.lower() == 'all':
        return platforms
    
    try:
        index = int(choice) - 1
        if 0 <= index < len(platforms):
            return [platforms[index]]
    except ValueError:
        pass
        
    print("Invalid choice.")
    return []

import random

def sanitize_username(domain):
    if not isinstance(domain, str): return "user"
    return re.sub(r'[^a-zA-Z0-9]', '_', domain.split('.')[0])

def generate_full_name(domain):
    if not isinstance(domain, str): return "User"
    return domain.split('.')[0].capitalize()

def generate_random_dob():
    year = random.randint(1975, 2000)
    month = random.randint(1, 12)
    day = random.randint(1, 28) # Safe for all months
    return f"{year}-{month:02d}-{day:02d}"

def generate_random_gender():
    return random.choice(["Male", "Female"])

def run_automation():
    print("=== Social Media Account Automation Started ===")
    
    target_platforms = get_platform_choice()
    if not target_platforms:
        print("No platform selected. Exiting.")
        return

    # 1. Read Excel
    try:
        df = pd.read_excel(INPUT_FILE)
    except FileNotFoundError:
        print(f"Error: {INPUT_FILE} not found.")
        return

    created_accounts = []

    with sync_playwright() as p:
        # Launch browser (Headless=False to allow manual intervention)
        browser = p.chromium.launch(headless=False, slow_mo=50)
        context = browser.new_context()

        for index, row in df.iterrows():
            email = row.get("Email")
            password = row.get("Password")
            webmail_url = row.get("Webmail")
            domain = row.get("Domain", "")
            
            if not email or not password:
                print(f"Skipping Row {index+1}: Missing Email or Password.")
                continue
                
            # Prepare User Data with defaults
            user_data = row.to_dict()
            if "Username" not in user_data or pd.isna(user_data["Username"]):
                user_data["Username"] = sanitize_username(str(domain))
            if "Full Name" not in user_data or pd.isna(user_data["Full Name"]):
                user_data["Full Name"] = generate_full_name(str(domain))
            if "Date of Birth (YYYY-MM-DD)" not in user_data or pd.isna(user_data["Date of Birth (YYYY-MM-DD)"]):
                user_data["Date of Birth (YYYY-MM-DD)"] = generate_random_dob()
            if "Gender" not in user_data or pd.isna(user_data["Gender"]):
                user_data["Gender"] = generate_random_gender()

            # Determine Platform(s) to run for this row? 
            # The user said "ask what platform I want to make an account for".
            # So we iterate through the selected platforms for each row.
            
            for platform_name in target_platforms:
                print(f"\n--- Processing Account: {email} | Platform: {platform_name} ---")
                
                bot_class = PLATFORM_MAP.get(platform_name)
                if not bot_class:
                    print(f"Platform '{platform_name}' logic not implemented yet.")
                    continue

                # Create a dedicated page for Social Media Sign Up
                social_page = context.new_page()
                
                # Instantiate Bot
                bot = bot_class(social_page, user_data)
                
                print("Step 1: Initiating Sign Up...")
                success = bot.sign_up()
                
                if success:
                    print("Step 2: Sign Up initiated. Paused for CAPTCHA/Verification.")
                    # The bot.sign_up() method already paused for manual CAPTCHA.
                    # Now we assume we are at the "Enter Code" screen.
                    
                    print("Step 3: Accessing Webmail for Verification Code...")
                    # Open a NEW page for Webmail to keep Social Page open
                    webmail_page = context.new_page()
                    webmail_bot = WebmailBot(webmail_page, email, password, webmail_url)
                    
                    # Fetch code
                    code = webmail_bot.login_and_get_code(platform_name)
                    webmail_page.close()
                    
                    if code:
                        print(f"Step 4: Entering verify code {code} into {platform_name}...")
                        # Assume all bots have enter_verification_code method or we add to base
                        if hasattr(bot, 'enter_verification_code'):
                            bot.enter_verification_code(code)
                        
                        # Final check or manual pause to ensure account is fully created
                        bot.wait_for_manual_action("Please verify the account is fully created, then press Enter.")
                        
                        # Record success
                        # Record success with ALL details
                        account_record = user_data.copy()
                        account_record.update({
                            "Platform": platform_name,
                            "Status": "Created",
                            "Notes": "Success",
                            "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                        })
                        created_accounts.append(account_record)
                    else:
                        print("Could not retrieve verification code automatically.")
                        account_record = user_data.copy()
                        account_record.update({
                            "Platform": platform_name,
                            "Status": "Failed",
                            "Notes": "Verification code not found",
                            "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                        })
                        created_accounts.append(account_record)
                else:
                     print("Sign up process failed or was aborted.")
                
                # Save progress immediately
                pd.DataFrame(created_accounts).to_excel(OUTPUT_FILE, index=False)
                print(f"Progress saved to {OUTPUT_FILE}")

                social_page.close()
            
            print(f"Finished processing {email}.")

        browser.close()

    # 2. Export Report
    print(f"\nSaving report to {OUTPUT_FILE}...")
    report_df = pd.DataFrame(created_accounts)
    report_df.to_excel(OUTPUT_FILE, index=False)
    print("Done.")

if __name__ == "__main__":
    run_automation()
