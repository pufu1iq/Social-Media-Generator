import pandas as pd
import os

def create_template():
    # Define columns based on common social media registration forms
    columns = [
        "Platform", # e.g., Twitter, LinkedIn, etc.
        "Email",
        "Password", 
        "Username",
        "Full Name",
        "Phone Number", # Optional, but often needed
        "Date of Birth (YYYY-MM-DD)",
        "Notes" # For storing backup codes or status
    ]
    
    # Create an empty DataFrame
    df = pd.DataFrame(columns=columns)
    
    # Add a sample row to guide the user
    sample_data = {
        "Platform": "Twitter",
        "Email": "example@email.com",
        "Password": "SecurePassword123!",
        "Username": "NewUser123",
        "Full Name": "John Doe",
        "Phone Number": "+1234567890",
        "Date of Birth (YYYY-MM-DD)": "1990-01-01",
        "Notes": "Sample row - delete before use"
    }
    
    df = pd.concat([df, pd.DataFrame([sample_data])], ignore_index=True)
    
    # Save to Excel
    output_file = "accounts_to_create.xlsx"
    if not os.path.exists(output_file):
        df.to_excel(output_file, index=False)
        print(f"Template created: {output_file}")
    else:
        print(f"File {output_file} already exists. Skipping creation.")

if __name__ == "__main__":
    create_template()
