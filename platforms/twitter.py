from .base import SocialPlatform
import time

class TwitterBot(SocialPlatform):
    def sign_up(self):
        self.log(f"Starting Twitter sign-up for {self.user_data['Username']}...")
        
        try:
            # Go to signup page
            self.page.goto("https://twitter.com/i/flow/signup")
            time.sleep(5) 
            
            # Click "Create account" if it appears
            self.click_element("div[role='button']:has-text('Create account')", timeout=5000)
            
            # Form Filling
            self.log("Filling initial form...")
            try:
                # Name
                self.fill_input("input[name='name']", self.user_data["Full Name"])
                
                # Use Email instead of Phone
                try:
                    self.page.click("text=Use email instead")
                    time.sleep(1)
                except:
                    pass 
                
                self.fill_input("input[name='email']", self.user_data["Email"])
                
                # DOB
                self.log("Attempting to fill DOB...")
                # Selectors for DOB are often tricky/dynamic. 
                # We will rely on manual intervention for complex select boxes if auto-fill fails.
                # However, let's try standard approach:
                dob = self.user_data.get("Date of Birth (YYYY-MM-DD)", "1990-01-01")
                year, month, day = dob.split("-")
                
                # Twitter uses select elements. Their IDs/Classes change, but they are usually the only 3 select elements in the modal.
                selects = self.page.query_selector_all("select")
                if len(selects) >= 3:
                     # Month (Index 0)
                     selects[0].select_option(value=str(int(month))) 
                     # Day (Index 1)
                     selects[1].select_option(value=str(int(day)))
                     # Year (Index 2)
                     selects[2].select_option(value=str(year))
                else:
                    self.log("Could not find 3 select elements for DOB. Skipping auto-fill.")

            except Exception as e:
                self.log(f"Form filling partial error: {e}")

            # Manual Intervention for CAPTCHA / Next Steps
            self.wait_for_manual_action("Please complete the CAPTCHA and proceed until you are asked for a Verification Code.")
            
            # At this point, the user should be on the Verification Code screen.
            # We return to Main loop to handle Webmail.
            return True

        except Exception as e:
            self.log(f"An error occurred during Twitter sign-up: {e}")
            return False

    def enter_verification_code(self, code):
        if not code:
            self.log("No code provided to enter.")
            return

        self.log(f"Entering verification code: {code}")
        try:
            self.fill_input("input[name='verif_code']", code)
            self.click_element("div[role='button']:has-text('Next')")
        except Exception as e:
            self.log(f"Error entering code: {e}")
            self.wait_for_manual_action("Please manually enter the code and finish the setup.")
