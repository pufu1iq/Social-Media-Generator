from .base import SocialPlatform
import time

class ThreadsBot(SocialPlatform):
    def sign_up(self):
        print(f"Starting Threads (Instagram) sign-up for {self.user_data['Username']}...")
        print("Note: Threads requires an Instagram account. We will attempt to sign up for Instagram.")
        
        try:
            self.page.goto("https://www.instagram.com/accounts/emailsignup/")
            
            self.page.wait_for_selector("input[name='emailOrPhone']", timeout=10000)
            
            self.fill_input("input[name='emailOrPhone']", self.user_data["Email"])
            print("Filled Email.")
            
            self.fill_input("input[name='fullName']", self.user_data["Full Name"])
            print("Filled Full Name.")
            
            self.fill_input("input[name='username']", self.user_data["Username"])
            print("Filled Username.")
            
            self.fill_input("input[name='password']", self.user_data["Password"])
            print("Filled Password.")
            
            self.click_button("button[type='submit']")
            
            # DOB usually comes next
            self.wait_for_manual_action("Please select your Birthday and enter the confirmation code sent to your email.")
            
            print("Threads/Instagram flow completed (partially manual).")

        except Exception as e:
            print(f"An error occurred during Threads sign-up: {e}")
