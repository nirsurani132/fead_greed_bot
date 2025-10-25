import requests
import os
import asyncio
from fear_and_greed_scraper import capture_fear_greed_gauge

async def send_fear_greed_image():
    webhook_url = os.getenv('WEBHOOK_URL')

    print("Capturing Fear & Greed image...")
    image_bytes = await capture_fear_greed_gauge()
    if image_bytes:
        files = {'file': ('fear_greed_gauge.png', image_bytes, 'image/png')}
        response = requests.post(webhook_url, files=files)
        if response.status_code == 204:
            print("Image sent successfully via webhook")
        else:
            print(f"Failed to send image: {response.status_code} - {response.text}")
    else:
        data = {'content': 'Failed to capture screenshot.'}
        response = requests.post(webhook_url, json=data)
        print("Failed message sent")

if __name__ == '__main__':
    asyncio.run(send_fear_greed_image())