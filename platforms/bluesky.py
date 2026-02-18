from .base import SocialPlatform
import time

class BlueskyBot(SocialPlatform):
    def sign_up(self):
        print(f"Starting Bluesky sign-up for {self.user_data['Username']}...")
        
        try:
            self.page.goto("https://bsky.app/")
            
            # Click "Create a new account"
            self.page.click("text=Create a new account") # Selector might be 'button' or 'a' with this text
            
            # Step 1: Hosting provider (Default is Bluesky Social) - Click Next
            try:
                self.page.click("text=Next", timeout=5000)
            except:
                print("Could not click first Next button (Hosting), maybe different flow.")

            # Step 2: Invite code (no longer needed for everyone, but might be present)
            # If invite code is not needed, we should see Email/Password fields.
            
            print("Waiting for Email input...")
            self.page.wait_for_selector("input[data-testid='emailInput']", timeout=10000)
            
            self.fill_input("input[data-testid='emailInput']", self.user_data["Email"])
            print("Filled Email.")
            
            self.fill_input("input[data-testid='passwordInput']", self.user_data["Password"])
            print("Filled Password.")
            
            # DOB - Bluesky has year/month/day inputs often
            self.fill_input("input[data-testid='dateOfBirthInput']", self.user_data["Date of Birth (YYYY-MM-DD)"]) # Check format
            
            self.click_button("text=Next")

            self.wait_for_manual_action("Please verify your handle and complete the signup process.")
            
            print("Bluesky flow completed (partially manual).")

        except Exception as e:
            print(f"An error occurred during Bluesky sign-up: {e}")
