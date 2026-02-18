# Social Media Account Automation

This tool helps you create accounts on multiple social media platforms by automating the initial form filling.

## Setup

1.  **Install dependencies**:
    (Already done if I set it up for you, but for reference)
    ```bash
    pip install -r requirements.txt
    playwright install chromium
    ```

2.  **Prepare Data**:
    - Open `accounts_to_create.xlsx`.
    - Fill in the account details (Platform, Username, Password, Email, etc.).
    - Supported Platforms (write these in the "Platform" column):
        - `Twitter` or `X`
        - `LinkedIn`
        - `TikTok`
        - `Pinterest`
        - `Bluesky`
        - `YouTube` (or `Google`)
        - `Threads` (or `Instagram`)

## How to Run

1.  Open your terminal.
2.  Run the script:
    ```bash
    python3 main.py
    ```
3.  **Watch the Browser**:
    - The script will open a browser window.
    - It will fill in the forms.
    - **IMPORTANT**: When it pauses (for CAPTCHA or Verification Code), go to the browser window, solve the puzzle or enter the code manually.
    - Press **Enter** in the terminal to continue to the next account after you are done.

## Notes

- **Security**: Do not share `accounts_to_create.xlsx` with anyone.
- **Manual Steps**: Automation handles the boring typing part. You handle the security/verification part.
