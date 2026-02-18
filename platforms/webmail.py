from playwright.sync_api import Page, TimeoutError
import time
import re

class WebmailBot:
    def __init__(self, page: Page, email: str, password: str, webmail_url: str):
        self.page = page
        self.email = email
        self.password = password
        self.webmail_url = webmail_url

    def log(self, message: str):
        print(f"[WEBMAIL] {message}")

    def login_and_get_code(self, platform_name: str) -> str:
        """
        Navigates to webmail, logs in, finds the email from definitions, and extracts code/link.
        Returns the code or link found.
        """
        self.log(f"Navigating to {self.webmail_url} for verification...")
        
        try:
            self.page.goto(self.webmail_url)
            self.page.wait_for_load_state("networkidle")
            
            # 1. Login Logic (Generic cPanel/Roundcube/Horde)
            # Most use 'user'/'email' and 'pass'/'password' inputs
            try:
                # Try standard selectors
                print("Filling Webmail credentials...")
                self.page.fill("input[name*='user'], input[name*='email'], input#user, input#rcmloginuser", self.email)
                self.page.fill("input[name*='pass'], input#pass, input#rcmloginpwd", self.password)
                
                print("Clicking Login...")
                # Try multiple common login button selectors
                login_selectors = [
                    "button#rcmloginsubmit", # Roundcube specific
                    "input#rcmloginsubmit",  # Roundcube specific
                    "button[type='submit']", 
                    "input[type='submit']", 
                    "#login_submit", 
                    "button:has-text('Login')", 
                    "button:has-text('Log in')",
                    "input[value='Login']"
                ]
                
                for selector in login_selectors:
                    try:
                        if self.page.locator(selector).first.is_visible(timeout=500):
                            self.page.click(selector)
                            self.log(f"Clicked login button: {selector}")
                            break
                    except:
                        pass
                        
                self.log("Login form submitted (or attempted).")
            except Exception as e:
                self.log(f"Login attempt failed (selectors might differ): {e}")
                input("Please manually log in to Webmail, then press Enter...")

            # 2. Wait for Inbox to load
            time.sleep(5) 
            
            # Handle "Open" button (common in cPanel -> Roundcube redirection)
            try:
                open_btn = self.page.get_by_text("Open", exact=True)
                if open_btn.is_visible():
                    open_btn.click()
                    self.log("Clicked 'Open' to enter Roundcube.")
                    time.sleep(3)
            except:
                pass

            # 3. Search for Email from the Platform
            self.log(f"Searching for email from {platform_name}...")
            # Reload to refresh inbox
            self.page.reload()
            time.sleep(3)

            # Define search keywords for each platform
            platform_keywords = {
                "Twitter": ["Twitter", "X", "verify"],
                "X": ["Twitter", "X", "verify"],
                "LinkedIn": ["LinkedIn", "PIN", "verification"],
                "TikTok": ["TikTok", "verification"],
                "Threads": ["Instagram", "Threads", "code"],  # Threads uses Instagram branding often
                "Pinterest": ["Pinterest", "confirm", "code"],
                "Bluesky": ["Bluesky", "code"],
                "YouTube": ["Google", "verification", "code"],
                "Google": ["Google", "verification", "code"],
            }
            
            keywords = platform_keywords.get(platform_name, [platform_name])
            
            # Construct a selector that looks for any of the keywords
            # This is a bit complex as we want "row containing any of these"
            # We will iterate and try to find the first match.
            
            email_item = None
            for keyword in keywords:
                 # Check for subject or sender containing the keyword
                 formatted_selector = f"tr:has-text('{keyword}'), div:has-text('{keyword}')"
                 found = self.page.locator(formatted_selector).first
                 if found.is_visible():
                     email_item = found
                     self.log(f"Found email match for keyword: {keyword}")
                     break
            
            if email_item is not None:
                if email_item.is_visible():
                    email_item.click()
                    self.log("Opened email.")
                    time.sleep(2)
                    
                    # 4. Extract Code
                    # Simple heuristic: look for 6-digit codes or "Verify" links
                    content = self.page.content()
                
                # Regex for 6-digit code
                code_match = re.search(r'\b\d{6}\b', content)
                if code_match:
                    code = code_match.group(0)
                    self.log(f"Found verification code: {code}")
                    return code
                
                self.log("No 6-digit code found. Checking for links needs manual handling or smarter parsing.")
                return input("Enter the code you found: ")
            else:
                self.log(f"No email found from {platform_name}.")
                print(f"Please find the email from {platform_name} manually, extract the code, and enter it below.")
                return input("Enter the code you found: ")

        except Exception as e:
            self.log(f"Webmail automation error: {e}")
            return input("Please manually check email and enter the code here: ")

    def get_imap_code(self, platform_name: str, imap_server: str = None) -> str:
        """
        Connects to IMAP server, searches for email, and extracts code.
        Only accepts emails received within the last 3.5 minutes (210s).
        """
        import imaplib
        import email
        from email.header import decode_header
        from email.utils import parsedate_to_datetime
        from datetime import datetime, timezone, timedelta
        
        self.log(f"Attempting IMAP verification for {platform_name}...")
        
        # Determine IMAP server if not provided
        # Heuristic: mail.domain.com
        if not imap_server:
            domain = self.email.split("@")[1]
            imap_server = f"mail.{domain}"
            
        self.log(f"Connecting to IMAP server: {imap_server}")
        
        try:
            # Connect
            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(self.email, self.password)
            mail.select("INBOX")
            
            # Search for emails
            # Keywords based on platform
            platform_keywords = {
                "Google": '(OR (SUBJECT "Google") (FROM "Google"))',
                "YouTube": '(OR (SUBJECT "Google") (FROM "Google"))',
                "Twitter": '(OR (SUBJECT "Twitter") (FROM "Twitter") (FROM "X"))',
                "X": '(OR (SUBJECT "Twitter") (FROM "Twitter") (FROM "X"))',
                "TikTok": '(OR (SUBJECT "TikTok") (FROM "TikTok"))',
            }
            
            criteria = platform_keywords.get(platform_name, f'(SUBJECT "{platform_name}")')
            
            self.log(f"Searching INBOX with criteria: {criteria}")
            status, messages = mail.search(None, criteria)
            
            if status != "OK":
                self.log("No messages found.")
                return None
                
            email_ids = messages[0].split()
            if not email_ids:
                self.log("No matching emails found via IMAP.")
                return None
                
            # Iterate backwards through emails (latest first) to find a recent valid one
            for email_id in reversed(email_ids):
                status, msg_data = mail.fetch(email_id, "(RFC822)")
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                # 1. Decode Subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8")
                
                self.log(f"Processing Email ID: {email_id.decode()} | Subject: {subject}")
                
                # --- SUBJECT FILTERING ---
                # Only accept emails that look like verification emails
                valid_subjects = ["verify", "verification", "code", "confirm", "security code", "google verification"]
                invalid_subjects = ["security alert", "sign-in", "signed in", "access", "welcome"]
                
                subject_lower = subject.lower()
                
                # Check for invalid subjects (Security Alerts often have codes but are not verification)
                if any(bad in subject_lower for bad in invalid_subjects):
                    self.log(f"Skipping email with invalid subject: {subject}")
                    continue
                    
                # Check for valid subjects (Allow generic if from Google, but prefer keywords)
                if not any(good in subject_lower for good in valid_subjects):
                     # If it's just "Google" from "Google", it might be valid.
                     # But "Security alert" is also from Google.
                     if "google" in subject_lower:
                         pass # Allow potentially generic Google subjects if they passed the invalid check
                     else:
                         self.log(f"Skipping email (Subject does not contain verify/code): {subject}")
                         continue

                # 2. Date Check (Recency)
                email_date_str = msg["Date"]
                if email_date_str:
                    try:
                        email_date = parsedate_to_datetime(email_date_str)
                        # Ensure timezone awareness for comparison
                        now = datetime.now(timezone.utc)
                        if email_date.tzinfo is None:
                            # Assume UTC if no timezone provided
                            email_date = email_date.replace(tzinfo=timezone.utc)
                            
                        # Calculate age
                        age = now - email_date
                        
                        if age.total_seconds() > 210: # 3.5 minutes
                            self.log(f"Skipping old email (Age: {int(age.total_seconds())}s > 210s).")
                            continue 
                    except Exception:
                        pass # Ignore date errors if subject is good
                
                # 3. Extract Body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        if "attachment" not in content_disposition:
                            if content_type == "text/plain":
                                body = part.get_payload(decode=True).decode()
                                break 
                            elif content_type == "text/html":
                                 body = part.get_payload(decode=True).decode()
                else:
                    body = msg.get_payload(decode=True).decode()
                    
                # 4. Extract Code (STRICT)
                # Look for G-XXXXXX or "code is XXXXXX"
                
                # Pattern: G-123456
                g_match = re.search(r'G-(\d{6})', body)
                if g_match:
                     code = g_match.group(1)
                     self.log(f"Found G-Code: {code}")
                     mail.close()
                     mail.logout()
                     return code
                
                # Pattern: "Verification code: 123456"
                # Matches: "code: 123456", "code is 123456", "code 123456"
                strict_match = re.search(r'(?i)(?:verification|verify|code)\D{0,10}(\d{6})', body)
                if strict_match:
                     code = strict_match.group(1)
                     self.log(f"Found Strict Code: {code}")
                     mail.close()
                     mail.logout()
                     return code

                # Fallback: Just 6 digits?
                # If subject has "verify" or "code", we should trust a 6-digit number found in the body.
                if any(k in subject_lower for k in ["verify", "code", "confirm", "google"]):
                    loose_match = re.search(r'\b(\d{6})\b', body)
                    if loose_match:
                        code = loose_match.group(1)
                        self.log(f"Found Loose Code (Subject Valid): {code}")
                        mail.close()
                        mail.logout()
                        return code
                        
                self.log(f"No valid code found. Body start: {body[:100].replace(chr(10), ' ')}...")
            
            self.log("No valid recent code found in any matching emails.")
            mail.close()
            mail.logout()
            return None

        except Exception as e:
            self.log(f"IMAP Error: {e}")
            return None
