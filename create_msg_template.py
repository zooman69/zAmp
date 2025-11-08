import win32com.client
import os

# Get the absolute path to the Images folder
script_dir = os.path.dirname(os.path.abspath(__file__))
images_folder = os.path.join(script_dir, "Images")
verification_image_path = os.path.join(images_folder, "zAmp verification")

# Check if image exists
if not os.path.exists(verification_image_path):
    print(f"Error: Image not found at {verification_image_path}")
    exit(1)

# Create Outlook application object
outlook = win32com.client.Dispatch("Outlook.Application")

# Create a new mail item
mail = outlook.CreateItem(0)  # 0 = olMailItem

# Set subject
mail.Subject = "zAmp and USB cable picture verification"

# Create HTML body with embedded image
# We'll use a content ID (cid) reference for the image
html_body = """
<html>
<head>
    <style>
        body { font-family: 'Calibri', sans-serif; font-size: 11pt; }
        p { margin: 10px 0; }
        ol { margin: 10px 0; padding-left: 25px; }
        li { margin: 8px 0; }
        .bold { font-weight: bold; }
    </style>
</head>
<body>
    <p>Hello,</p>

    <p>To accurately diagnose the issue with your zAmp, please provide clear pictures of the following:</p>

    <ol>
        <li><span class="bold">zAmp</span>:<br>
        A photo of the back of the zAmp, clearly showing the serial number and the USB cable plugged into the zAmp.</li>

        <li><span class="bold">Monoprice USB Cable</span>:<br>
        A close-up photo of the Monoprice USB cable, focusing on the section with the "Monoprice" logo.</li>

        <li><span class="bold">System Setup</span>:<br>
        A picture of your system setup with the USB cable connected to both the zAmp and the system.</li>
    </ol>

    <p>Please refer to the image below for examples of the requested photos. Once you have taken these pictures, send them to <a href="mailto:support@neuroptimal.com">support@neuroptimal.com</a></p>

    <p>Thank you for your cooperation.</p>

    <p><img src="cid:verification_image" style="max-width: 100%; height: auto; border: 1px solid #000000;"></p>
</body>
</html>
"""

mail.HTMLBody = html_body

# Attach the image with content ID
attachment = mail.Attachments.Add(verification_image_path)
attachment.PropertyAccessor.SetProperty("http://schemas.microsoft.com/mapi/proptag/0x3712001F", "verification_image")

# Save as .msg file in Templates folder
templates_folder = os.path.join(script_dir, "Templates")
if not os.path.exists(templates_folder):
    os.makedirs(templates_folder)

msg_file_path = os.path.join(templates_folder, "zAmp_Verification_Request_ENGLISH.msg")
mail.SaveAs(msg_file_path, 3)  # 3 = olMSG format

print(f"Email template saved to: {msg_file_path}")
print(f"\nYou can now:")
print(f"1. Double-click the .msg file to open it in Outlook")
print(f"2. Fill in the 'To:' field with the recipient")
print(f"3. Click Send")
