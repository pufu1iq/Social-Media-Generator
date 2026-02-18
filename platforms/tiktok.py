from .base import SocialPlatform
import time

class TikTokBot(SocialPlatform):
    def sign_up(self):
        print(f"Starting TikTok sign-up for {self.user_data['Username']}...")
        
        try:
            self.page.goto("https://www.tiktok.com/signup")
            
            # 0. Handle Overlays (Cookies, Privacy Policy)
            print("Checking for overlays...")
            try:
                # Cookie Banner
                if self.page.locator("button:has-text('Allow all')").is_visible():
                    print("Clicking 'Allow all' cookies...")
                    self.page.click("button:has-text('Allow all')")
                    time.sleep(1)
                elif self.page.locator("button:has-text('Decline optional cookies')").is_visible():
                    print("Clicking 'Decline optional cookies'...")
                    self.page.click("button:has-text('Decline optional cookies')")
                    time.sleep(1)
                    
                # Privacy/EEA Update Banner ("Got it")
                if self.page.locator("text=Got it").is_visible():
                     print("Dismissing 'Got it' banner...")
                     self.page.click("text=Got it")
                     time.sleep(1)
            except Exception as e:
                print(f"Overlay handling warning: {e}")

            # 1. Click "Use phone or email"
            print("Looking for 'Use phone or email' option...")
            try:
                # Try generic text selector with FORCE click
                selector = "div:has-text('Use phone or email')"
                self.page.wait_for_selector(selector, timeout=5000)
                
                # Highlight for debug visibility
                self.page.evaluate(f"document.querySelector(\"{selector}\").style.border = '5px solid red'")
                
                print(f"Found element. Attempting Force Click on: {selector}")
                self.page.click(selector, force=True)
                
                # Verify if we moved?
                time.sleep(2)
                if self.page.locator("text=Sign up with email").is_visible() or self.page.locator("input[name='email']").is_visible():
                    print("Successfully entered sign-up form.")
                else:
                    print("Force click didn't work. Trying JavaScript click...")
                    # Fallback to JS Click
                    self.page.evaluate(f"document.querySelector(\"a[href*='phone-or-email'], div:has-text('Use phone or email')\").click()")
                    
            except Exception as e:
                print(f"Entry button click failed: {e}")
                print("Trying fallback selector specific to TikTok's link...")
                try:
                    self.page.click("a[href*='/signup/phone-or-email']", force=True)
                except:
                     print("All auto-click methods failed. Please click 'Use phone or email' MANUALLY now.")

            # 2. Fill DOB (Date of Birth)
            print("Step: Filling Date of Birth...")
            # TikTok usually uses 3 dropdowns: Month, Day, Year.
            # Selectors are tricky, often div[aria-label='Month'] or similar.
            # Strategy: Click to open, then type or select.
            
            dob = self.user_data.get("Date of Birth (YYYY-MM-DD)", "1999-01-01")
            year, month, day = dob.split("-")
            month_int = int(month)
            month_name = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"][month_int - 1]
            
            try:
                # Wait for container
                self.page.wait_for_selector("div:has-text('When’s your birthday?')", timeout=10000)
                
                # Month
                print(f"Setting Month: {month_name}")
                self.page.click("div[aria-label='Month']")
                self.page.keyboard.type(month_name)
                self.page.keyboard.press("Enter")
                time.sleep(0.5)

                # Day
                print(f"Setting Day: {day}")
                self.page.click("div[aria-label='Day']")
                self.page.keyboard.type(str(int(day))) # Remove leading zero
                self.page.keyboard.press("Enter")
                time.sleep(0.5)
                
                # Year
                print(f"Setting Year: {year}")
                self.page.click("div[aria-label='Year']")
                self.page.keyboard.type(str(year))
                self.page.keyboard.press("Enter")
                time.sleep(0.5)
                
            except Exception as e:
                print(f"DOB filling failed: {e}")
                self.wait_for_manual_action("Please manually set the Date of Birth.")

            # 3. Switch to Email
            print("Step: Switching to Email sign-up...")
            try:
                # Look for "Sign up with email" link/text usually on the top right of the form or a tab
                self.page.click("text=Sign up with email")
            except:
                print("Could not click 'Sign up with email'. Check if already active.")

            # 4. Fill Email and Password
            print("Step: Filling Credentials...")
            try:
                email_val = self.user_data['Email']
                password_val = self.user_data['Password']
                
                self.fill_input("input[name='email']", email_val)
                self.fill_input("input[type='password']", password_val)
                
            except Exception as e:
                print(f"Credential filling failed: {e}") 
                
            # 5. Send Code
            print("Step: Requesting Verification Code...")
            try:
                # "Send code" button inside the verification input container
                self.page.click("button:has-text('Send code')")
                
                # Wait for code to be sent (and potential CAPTCHA)
                print("Waiting for captcha or code sent...")
                # TikTok often shows a slider captcha here. 
                # We can't solve it automatically easily.
                self.wait_for_manual_action("Please solve the TikTok Slider Captcha if it appeared.")
                
                # 6. Retrieve Code via IMAP
                print("Step: Retrieving TikTok Code...")
                 # Infer IMAP server
                domain = email_val.split("@")[1]
                imap_server = f"mail.{domain}"
                
                from .webmail import WebmailBot
                webmail_bot = WebmailBot(self.page, email_val, password_val, "")
                
                code = None
                for i in range(3):
                    print(f"Checking email (Attempt {i+1}/3)...")
                    code = webmail_bot.get_imap_code("TikTok", imap_server=imap_server)
                    if code:
                        break
                    time.sleep(10)
                
                if code:
                    print(f"Found code: {code}")
                    self.fill_input("input[placeholder='Enter 6-digit code']", code)
                    
                    # Click Next or Sign up
                    print("Clicking Next/Sign up...")
                    try:
                        self.click_button("button:has-text('Next')")
                    except:
                        print("'Next' button not found, trying 'Sign up'...")
                        try:
                            self.click_button("button:has-text('Sign up')")
                        except:
                            print("Could not auto-click Next/Sign up. Please click manually.")
                            
                else:
                    print("Code not found via IMAP.")
                    self.wait_for_manual_action("Please manually check email and enter code.")
                    
            except Exception as e:
                print(f"Verification flow error: {e}")
                self.wait_for_manual_action("Please complete the verification step manually.")
                
            # Final Manual Check
            self.wait_for_manual_action("Please complete any remaining steps (Username setup) and verify account is created.")
            print("TikTok flow completed.")

        except Exception as e:
            print(f"An error occurred during TikTok sign-up: {e}")
