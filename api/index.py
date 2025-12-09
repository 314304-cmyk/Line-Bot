from flask import Flask, request, abort
import os
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

app = Flask(__name__)

# LINE Bot credentials from environment variables
configuration = Configuration(access_token=os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', ''))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET', ''))

# Customer service keyword responses
CUSTOMER_SERVICE_RESPONSES = {
    '服務時間': '🕐 我們的服務時間：\n週一至週五：09:00 - 18:00\n週六：10:00 - 16:00\n週日及國定假日休息',
    '營業時間': '🕐 我們的服務時間：\n週一至週五：09:00 - 18:00\n週六：10:00 - 16:00\n週日及國定假日休息',
    '聯絡方式': '📞 聯絡我們：\n電話：02-1234-5678\nEmail：service@example.com\n地址：台北市信義區xxx路xx號',
    '聯繫': '📞 聯絡我們：\n電話：02-1234-5678\nEmail：service@example.com\n地址：台北市信義區xxx路xx號',
    '價格': '💰 價格資訊：\n請參考我們的官網價格頁面，或來電洽詢專人為您報價。\n官網：https://example.com/pricing',
    '費用': '💰 價格資訊：\n請參考我們的官網價格頁面，或來電洽詢專人為您報價。\n官網：https://example.com/pricing',
    '幫助': '📋 您好！我可以幫您處理以下問題：\n\n🔹 輸入「服務時間」查詢營業時間\n🔹 輸入「聯絡方式」取得聯絡資訊\n🔹 輸入「價格」了解價格資訊\n\n如需其他協助，請直接描述您的問題！',
    'help': '📋 您好！我可以幫您處理以下問題：\n\n🔹 輸入「服務時間」查詢營業時間\n🔹 輸入「聯絡方式」取得聯絡資訊\n🔹 輸入「價格」了解價格資訊\n\n如需其他協助，請直接描述您的問題！',
}

DEFAULT_RESPONSE = '感謝您的訊息！\n\n如需快速查詢，您可以輸入以下關鍵字：\n🔹 服務時間\n🔹 聯絡方式\n🔹 價格\n🔹 幫助\n\n或稍候將有專人為您服務。'


def get_response(user_message: str) -> str:
    """Get appropriate response based on user message."""
    # Check for keyword matches
    for keyword, response in CUSTOMER_SERVICE_RESPONSES.items():
        if keyword in user_message:
            return response
    
    # Return default response if no keyword matched
    return DEFAULT_RESPONSE


@app.route('/api/webhook', methods=['POST'])
def webhook():
    """Handle LINE webhook requests."""
    # Get X-Line-Signature header value
    signature = request.headers.get('X-Line-Signature', '')
    
    # Get request body as text
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    """Handle incoming text messages."""
    user_message = event.message.text
    response = get_response(user_message)
    
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response)]
            )
        )


# For local development
if __name__ == '__main__':
    app.run(debug=True, port=5000)
