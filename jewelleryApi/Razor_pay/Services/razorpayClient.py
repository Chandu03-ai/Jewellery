import os
import razorpay
from dotenv import load_dotenv

load_dotenv()

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_SECRET = os.getenv("RAZORPAY_SECRET")

if not RAZORPAY_KEY_ID or not RAZORPAY_SECRET:
    raise ValueError("Razorpay API credentials are not set in environment variables.")

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_SECRET))
