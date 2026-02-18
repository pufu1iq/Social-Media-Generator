from .base import SocialPlatform
import time

class YouTubeBot(SocialPlatform):
    def sign_up(self):
        print(f"Starting YouTube (Google) sign-up for {self.user_data['Username']}...")
        print("Note: Google has very strict bot detection. You will likely need to verify via phone immediately.")
        
        try:
            self.page.goto("https://accounts.google.com/signup")
            
            # First Name / Last Name
            self.page.wait_for_selector("input[name='firstName']", timeout=10000)
            
            full_name = self.user_data["Full Name"].split(" ")
            first_name = full_name[0]
            last_name = " ".join(full_name[1:]) if len(full_name) > 1 else "."
            
            self.fill_input("input[name='firstName']", first_name)
            self.fill_input("input[name='lastName']", last_name)
            
            self.click_button("span:has-text('Next')")
            
            dob = self.user_data.get("Date of Birth (YYYY-MM-DD)", "1990-01-01")
            year, month, day = dob.split("-")

            # Basic Info (DOB, Gender)
            print("Waiting for Basic Info (DOB/Gender)...")
            
            # Anchor Strategy: Find 'Day' or 'Year' input which are usually standard <input> fields.
            # Then navigate relative to them.
            
            # Wait for Day or Year
            try:
                self.page.wait_for_selector("input#day, input[name='day'], input[aria-label*='Day'], input#year, input[name='year']", timeout=10000)
            except:
                print("Could not find Day/Year anchor. Trying to find 'Basic info' text...")
                try:
                    self.page.wait_for_selector("text='Basic info'", timeout=3000)
                except:
                    print("Could not find Basic Info text either. attempting blind tab navigation.")

            dob = self.user_data.get("Date of Birth (YYYY-MM-DD)", "1990-01-01")
            year, month, day = dob.split("-")
            month_int = int(month)
            month_name = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"][month_int - 1]
            gender = self.user_data.get("Gender", "Male")

            print(f"Filling DOB: {day} {month_name} {year}, Gender: {gender}")

            try:
                # 1. Fill Day and Year first (most reliable)
                # Try to fill Day
                day_filled = False
                try:
                    self.fill_input("input#day, input[name='day']", str(int(day)), timeout=2000)
                    day_filled = True
                except:
                    pass

                # Try to fill Year
                year_filled = False
                try:
                    self.fill_input("input#year, input[name='year']", str(year), timeout=2000)
                    year_filled = True
                except:
                    pass

                # 2. Handle Month (Relative to Day)
                # If we successfully found Day, Month is usually one Shift+Tab away.
                if day_filled:
                    print("Navigating to Month from Day...")
                    self.page.click("input#day, input[name='day']")
                    self.page.keyboard.press("Shift+Tab")
                    time.sleep(0.5)
                    # Now in Month. Open it.
                    self.page.keyboard.press("Space")
                    time.sleep(0.5)
                    # Type Month Name
                    self.page.keyboard.type(month_name)
                    time.sleep(0.5)
                    self.page.keyboard.press("Enter")
                else:
                    print("Could not anchor to Day for Month. Skipping Month fill (might fail).")

                # 3. Handle Gender (Relative to Year)
                # If we found Year, Gender is usually one Tab away.
                if year_filled:
                    print("Navigating to Gender from Year...")
                    self.page.click("input#year, input[name='year']")
                    self.page.keyboard.press("Tab")
                    time.sleep(0.5)
                    # Now in Gender. Open it.
                    self.page.keyboard.press("Space")
                    time.sleep(0.5)
                    # Type Gender or Arrow Down
                    # "Female" starts with F, "Male" starts with M. 
                    # Typing the letter often identifies it.
                    self.page.keyboard.type(gender[0]) 
                    time.sleep(0.5)
                    self.page.keyboard.press("Enter")
                else:
                     print("Could not anchor to Year for Gender. Skipping Gender fill.")

            except Exception as e:
                 print(f"Relational fill failed: {e}")

            print("Filled Basic Info (Relational Strategy).")
            
            # Click Next after Basic Info
            try:
                self.click_button("span:has-text('Next')")
            except:
                self.page.keyboard.press("Enter")
            
            # --- NEW STEP: Choose Email Address ---
            print("Step: Email Selection...")
            try:
                # User observation: Field is already focused. Just type.
                time.sleep(2) # Give page a moment to load
                
                existing_email = self.user_data['Email']
                print(f"Typing email check: {existing_email}")
                
                # Check if we need to click "Use my current email address instead" just in case
                # But prioritize typing if focused.
                
                # Try typing directly
                self.page.keyboard.type(existing_email)
                time.sleep(1)
                
                # Press Enter or Click Next
                print("Pressing Enter/Next...")
                try:
                    self.click_button("span:has-text('Next')")
                except:
                    self.page.keyboard.press("Enter")
                    
            except Exception as e:
                print(f"Email fill failed: {e}")
                self.wait_for_manual_action("Please manually enter the email from Excel and click Next.")
            
            # --- NEW STEP: Webmail Verification (IMAP) ---
            print("Step: Verifying Email Code (via IMAP)...")
            try:
                # Wait for "Enter code" input
                code_input_selector = "input[name='code'], input[id='code'], input[aria-label*='code']"
                try:
                    self.page.wait_for_selector(code_input_selector, timeout=20000) # Give it time to arrive
                    print("Found Verification Code input field.")
                except:
                     print("Could not find code input. Checking if we are on phone verify...")
                     if self.page.locator("input[type='tel']").is_visible():
                         print("Detected Phone Verification. Manual intervention required.")
                         self.wait_for_manual_action("Please verify phone number manually.")
                         return
                     else:
                         print("Proceeding safely...")

                # IMAP Logic
                email_user = self.user_data.get('Email')
                email_pass = self.user_data.get('Password')
                
                # Infer IMAP server from Email or use 'Webmail' column if it looks like a server
                # Heuristic: if email is user@epartner.ro -> mail.epartner.ro
                domain = email_user.split("@")[1]
                imap_server = f"mail.{domain}"
                
                print(f"Connecting to IMAP: {imap_server} for {email_user}...")
                
                from .webmail import WebmailBot
                # We don't need a page for IMAP only, but the class asks for it. Passing current page is fine or None.
                webmail_bot = WebmailBot(self.page, email_user, email_pass, "")
                
                # Retry loop for IMAP code
                verification_code = None
                for i in range(3):
                    print(f"Checking email (Attempt {i+1}/3)...")
                    verification_code = webmail_bot.get_imap_code("Google", imap_server=imap_server)
                    if verification_code:
                        break
                    time.sleep(5) # Wait for email to arrive
                
                if verification_code:
                    print(f"Entering verification code: {verification_code}")
                    self.fill_input(code_input_selector, verification_code)
                    
                    try:
                        self.click_button("span:has-text('Next')")
                    except:
                        self.page.keyboard.press("Enter")
                else:
                    print("Failed to retrieve code via IMAP.")
                    self.wait_for_manual_action("Please check webmail manually and enter the code.")

            except Exception as e:
                print(f"IMAP verification failed: {e}")
                self.wait_for_manual_action("Please complete verification manually.")
            
            # --- NEW STEP: Create Password ---
            print("Step: Creating Password...")
            try:
                # Wait for password input
                # usually input[name='Passwd']
                password_selector = "input[name='Passwd'], input[type='password'], input[name='password']"
                confirm_selector = "input[name='PasswdAgain'], input[name='confirm_password']"
                
                self.page.wait_for_selector(password_selector, timeout=10000)
                
                password = self.user_data.get('Password')
                if not password:
                    print("Error: No password found in Excel.")
                    raise ValueError("Missing Password")
                    
                print(f"Filling Password...")
                self.fill_input(password_selector, password)
                
                # Check for Confirm Password
                if self.page.locator(confirm_selector).is_visible():
                    print("Filling Confirm Password...")
                    self.fill_input(confirm_selector, password)
                    
                # Click Next
                print("Clicking Next after password...")
                try:
                    self.click_button("span:has-text('Next')")
                except:
                    self.page.keyboard.press("Enter")
                
                # Check for "Something went wrong" error
                time.sleep(2)
                if self.page.locator("text='Something went wrong'").is_visible():
                    print("Detected 'Something went wrong' error.")
                    self.wait_for_manual_action("Google flagged the request. Please manually resolve the error (try clicking Next again or changing IP) and press Enter.")

            except Exception as e:
                print(f"Password step failed: {e}")
                self.wait_for_manual_action("Please manually enter the password from Excel.")

            # Verify Phone - Google almost always asks for this now.
            self.wait_for_manual_action("Google likely requires Phone Verification now. Please complete it manually.")
            
            print("YouTube/Google flow completed (partially manual).")

        except Exception as e:
            print(f"An error occurred during YouTube sign-up: {e}")
