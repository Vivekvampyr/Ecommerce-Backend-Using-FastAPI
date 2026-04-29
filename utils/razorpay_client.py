import razorpay
from config import settings

# Single Shared Client - import this everywhere
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))