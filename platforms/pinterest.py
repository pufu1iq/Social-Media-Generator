from .base import SocialPlatform
import time

class PinterestBot(SocialPlatform):
    def sign_up(self):
        print(f"Starting Pinterest sign-up for {self.user_data['Username']}...")
        
        try:
            self.page.goto("https://www.pinterest.com/business/create/") # Business account is often easier but let's try standard personal if possible, or just business as it's for 'clients'.
            # Actually, let's try the consumer signup
            self.page.goto("https://www.pinterest.com/signup/")
            
            self.page.wait_for_selector("input[id='email']", timeout=10000)
            
            # Fill Email
            self.fill_input("input[id='email']", self.user_data["Email"])
            print("Filled Email.")
            
            # Fill Password
            self.fill_input("input[id='password']", self.user_data["Password"])
            print("Filled Password.")
            
            # Birthdate
            self.fill_input("input[id='birthdate']", self.user_data["Date of Birth (YYYY-MM-DD)"])
            print("Filled Birthdate.")
            
            # Click Continue
            self.click_button("button:has-text('Continue')")

            # Pinterest often asks for gender next
            self.wait_for_manual_action("Please select gender and complete any CAPTCHA/Interests selection.")
            
            print("Pinterest flow completed (partially manual).")

        except Exception as e:
            print(f"An error occurred during Pinterest sign-up: {e}")
