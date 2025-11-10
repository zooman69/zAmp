# FemibyJojo Wix Site HTML Extraction

## How to Extract HTML from Your Wix Site

Since Wix sites are dynamically rendered, you need to extract the HTML from the live site after it loads in your browser.

### Method 1: Using the Extraction Script

1. Open **femibyjojo.com** in your browser
2. Open Developer Tools (Press `F12` or `Right Click → Inspect`)
3. Go to the **Console** tab
4. Copy and paste the contents of `extract-wix-html.js` into the console
5. Press Enter
6. Wait 3 seconds - a JSON file will download with all extracted content
7. The full HTML will also be logged in the console

### Method 2: Manual Extraction via Browser

1. Visit **femibyjojo.com**
2. Wait for the page to fully load
3. Right-click anywhere on the page
4. Select "View Page Source" or press `Ctrl+U`
5. Copy all the HTML (Ctrl+A, Ctrl+C)
6. Save to a file

### Method 3: Using Browser DevTools

1. Visit **femibyjojo.com**
2. Press `F12` to open Developer Tools
3. Go to the **Elements** tab
4. Right-click on `<html>` at the top
5. Select "Copy" → "Copy outerHTML"
6. Paste into a text editor and save

## What Can You Modify?

Once you have the HTML structure, you can:

1. **Add Custom Code via Wix Editor**:
   - Log into your Wix dashboard
   - Go to Settings → Custom Code
   - Add HTML/CSS/JavaScript snippets

2. **Use Wix Embed Elements**:
   - In the Wix editor, add an "HTML iframe" or "Embed Code" element
   - Paste your custom HTML/CSS/JavaScript

3. **Modify Specific Elements**:
   - Identify element IDs or classes from the extracted HTML
   - Use custom CSS to override styles
   - Use custom JavaScript to modify behavior

## Need Help?

Let me know which specific elements you want to modify and I can help you create the custom code to inject via Wix's Custom Code feature.
