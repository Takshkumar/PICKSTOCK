import pyperclip
import requests
import time
import threading
from datetime import datetime

class ClipboardToTelegram:
    def __init__(self):
        # Configuration - Replace these with your actual values
        self.BOT_TOKEN = "7205248528:AAGQGwWlO4lOwZ1Q7k20gZ0DfjNxPT-dcx0"  # Provided bot token
        self.CHAT_ID = "5462118681"     # Provided chat ID
        
        # Telegram API URLs
        self.send_url = f"https://api.telegram.org/bot{self.BOT_TOKEN}/sendMessage"
        self.updates_url = f"https://api.telegram.org/bot{self.BOT_TOKEN}/getUpdates"
        
        # Store the last clipboard content to avoid duplicate sends
        self.last_clipboard = ""
        
        # Store last update ID to avoid processing same messages
        self.last_update_id = 0
        
        # Running flag
        self.running = True
        
        # Check if configuration is set
        self.check_config()
    
    def check_config(self):
        """Check if bot token and chat ID are configured"""
        if self.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or self.CHAT_ID == "YOUR_CHAT_ID_HERE":
            print("⚠️  ERROR: Please configure your BOT_TOKEN and CHAT_ID in the script!")
            print("\n📝 Steps to configure:")
            print("1. Open the script file")
            print("2. Replace 'YOUR_BOT_TOKEN_HERE' with your actual bot token")
            print("3. Replace 'YOUR_CHAT_ID_HERE' with your actual chat ID")
            print("\n🔧 How to get Bot Token:")
            print("- Message @BotFather on Telegram")
            print("- Send /newbot and follow instructions")
            print("- Copy the token you receive")
            print("\n🆔 How to get Chat ID:")
            print("- Send any message to your bot")
            print("- Open this URL in browser (replace YOUR_BOT_TOKEN):")
            print("  https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates")
            print("- Look for 'chat':{'id': YOUR_CHAT_ID}")
            input("\nPress Enter after configuring...")
            exit(1)
    
    def test_connection(self):
        """Test Telegram connection"""
        print("🔄 Testing Telegram connection...")
        try:
            test_message = "🤖 Bot connected successfully! Ready to monitor clipboard."
            data = {
                'chat_id': self.CHAT_ID,
                'text': test_message
            }
            
            response = requests.post(self.send_url, data=data, timeout=10)
            
            if response.status_code == 200:
                print("✅ Telegram connection successful!")
                return True
            else:
                print(f"❌ Telegram connection failed!")
                print(f"Status Code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    def send_to_telegram(self, message):
        """Send message to Telegram"""
        try:
            data = {
                'chat_id': self.CHAT_ID,
                'text': message
            }
            
            response = requests.post(self.send_url, data=data, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Sent to Telegram: {message[:50]}{'...' if len(message) > 50 else ''}")
                return True
            else:
                print(f"❌ Failed to send. Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Send error: {e}")
            return False
    
    def get_telegram_updates(self):
        """Get updates from Telegram"""
        try:
            params = {
                'offset': self.last_update_id + 1,
                'timeout': 1  # Shorter timeout for responsiveness
            }
            
            response = requests.get(self.updates_url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    return data.get('result', [])
            return []
                
        except Exception as e:
            print(f"❌ Update error: {e}")
            return []
    
    def handle_paste_command(self, text):
        """Handle /paste command from Telegram"""
        try:
            if len(text) > 6:  # More than just "/paste"
                paste_content = text[6:].strip()  # Remove "/paste " from beginning
                
                if paste_content:
                    # Copy to clipboard
                    pyperclip.copy(paste_content)
                    print(f"📋 Copied to clipboard: {paste_content[:50]}{'...' if len(paste_content) > 50 else ''}")
                    
                    # Send confirmation
                    confirmation = f"✅ Copied to clipboard!"
                    self.send_to_telegram(confirmation)
                else:
                    self.send_to_telegram("ℹ️ Usage: /paste <your message>")
            else:
                self.send_to_telegram("ℹ️ Usage: /paste <your message>")
                
        except Exception as e:
            print(f"❌ Paste error: {e}")
            self.send_to_telegram("❌ Error copying to clipboard")
    
    def monitor_clipboard(self):
        """Monitor clipboard for changes"""
        print("📋 Starting clipboard monitoring...")
        
        # Get initial clipboard
        try:
            self.last_clipboard = pyperclip.paste() or ""
        except:
            self.last_clipboard = ""
        
        while self.running:
            try:
                current_clipboard = pyperclip.paste() or ""
                
                # Check if clipboard changed and is not empty
                if (current_clipboard != self.last_clipboard and 
                    current_clipboard.strip() != ""):
                    
                    print(f"📋 New clipboard: {current_clipboard[:50]}{'...' if len(current_clipboard) > 50 else ''}")
                    
                    if self.send_to_telegram(current_clipboard):
                        self.last_clipboard = current_clipboard
                
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Clipboard monitor error: {e}")
                time.sleep(2)
    
    def monitor_telegram(self):
        """Monitor Telegram for commands"""
        print("📱 Starting Telegram monitoring...")
        
        while self.running:
            try:
                updates = self.get_telegram_updates()
                
                for update in updates:
                    update_id = update.get('update_id', 0)
                    
                    if update_id > self.last_update_id:
                        self.last_update_id = update_id
                        
                        message = update.get('message', {})
                        text = message.get('text', '')
                        chat_id = str(message.get('chat', {}).get('id', ''))
                        
                        # Only process messages from configured chat
                        if chat_id == str(self.CHAT_ID) and text.startswith('/paste'):
                            print(f"📱 Received command: {text}")
                            self.handle_paste_command(text)
                
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ Telegram monitor error: {e}")
                time.sleep(5)
    
    def start(self):
        """Start the bot"""
        print("🤖 Clipboard ↔️ Telegram Bot Starting...")
        print("=" * 50)
        
        # Test connection first
        if not self.test_connection():
            print("❌ Cannot start - connection failed!")
            return
        
        print("\n✅ Bot is running!")
        print("📋 Copy text → Goes to Telegram")
        print("📱 Send '/paste <text>' in Telegram → Goes to clipboard")
        print("🛑 Press Ctrl+C to stop")
        print("=" * 50)
        
        # Start monitoring threads
        clipboard_thread = threading.Thread(target=self.monitor_clipboard, daemon=True)
        telegram_thread = threading.Thread(target=self.monitor_telegram, daemon=True)
        
        clipboard_thread.start()
        telegram_thread.start()
        
        try:
            # Keep main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping bot...")
            self.running = False
            print("👋 Bot stopped!")

def main():
    """Main function"""
    # Check dependencies
    try:
        import pyperclip
        import requests
    except ImportError:
        print("❌ Missing required packages!")
        print("Run this command:")
        print("pip install pyperclip requests")
        return
    
    # Test clipboard access
    try:
        pyperclip.copy("test")
        pyperclip.paste()
        print("✅ Clipboard access working")
    except Exception as e:
        print(f"❌ Clipboard access failed: {e}")
        print("💡 Try installing: pip install pyperclip")
        return
    
    # Start bot
    bot = ClipboardToTelegram()
    bot.start()

if __name__ == "__main__":
    main()