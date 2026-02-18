from playwright.sync_api import Page, TimeoutError

class SocialPlatform:
    def __init__(self, page: Page, user_data: dict, debug_mode: bool = True):
        self.page = page
        self.user_data = user_data
        self.debug_mode = debug_mode

    def log(self, message: str):
        if self.debug_mode:
            print(f"[BOT] {message}")

    def wait_for_manual_action(self, message: str = "Please perform manual action."):
        """
        Pauses execution for manual intervention (CAPTCHA, OTP).
        """
        print(f"\n[MANUAL INTERVENTION REQUIRED] {message}")
        input("Press Enter to continue after you have completed the action...")

    def click_element(self, selector: str, timeout: int = 5000):
        try:
            self.page.wait_for_selector(selector, state="visible", timeout=timeout)
            self.page.click(selector)
            self.log(f"Clicked {selector}")
        except TimeoutError:
            self.log(f"Warning: Could not find element {selector}")

    def click_button(self, selector: str, timeout: int = 5000):
        self.click_element(selector, timeout)

    def fill_input(self, selector: str, value: str, timeout: int = 5000):
        try:
            self.page.wait_for_selector(selector, state="visible", timeout=timeout)
            self.page.fill(selector, str(value))
            self.log(f"Filled {selector}")
        except TimeoutError:
            self.log(f"Warning: Could not find input {selector}")
