from .base import SocialPlatform
import time

class LinkedInBot(SocialPlatform):
    def sign_up(self):
        print(f"Starting LinkedIn sign-up for {self.user_data['Username']}...")
        
        try:
            self.page.goto("https://www.linkedin.com/signup")
            # Wait for load
            self.page.wait_for_selector("input[name='email-or-phone']", timeout=10000)
            
            # Fill Email
            self.fill_input("input[name='email-or-phone']", self.user_data["Email"])
            print("Filled Email.")
            
            # Fill Password
            self.fill_input("input[name='password']", self.user_data["Password"])
            print("Filled Password.")
            
            # Click Agree & Join
            self.click_button("button#join-form-submit")
            
            # First Name / Last Name usually appears next
            print("Waiting for Name fields...")
            try:
                self.page.wait_for_selector("input[name='first-name']", timeout=10000)
                
                # Split Full Name
                full_name = self.user_data["Full Name"].split(" ")
                first_name = full_name[0]
                last_name = " ".join(full_name[1:]) if len(full_name) > 1 else "."
                
                self.fill_input("input[name='first-name']", first_name)
                self.fill_input("input[name='last-name']", last_name)
                print("Filled Name.")
                
                self.click_button("button#join-form-submit") # Button ID might match or be different
                
            except Exception as e:
                print(f"Could not find or fill Name fields (might be a different flow): {e}")

            # LinkedIn often asks for Verification / Captcha immediately here.
            self.wait_for_manual_action("Please solve the LinkedIn security verification (puzzle) manually.")
            
            print("LinkedIn flow completed (partially manual).")

        except Exception as e:
            print(f"An error occurred during LinkedIn sign-up: {e}")
