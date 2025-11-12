"""
Momo Payment Integration
"""
import requests
import json
import hashlib
import hmac
from datetime import datetime
import os

class MomoPayment:
    def __init__(self, partner_code, access_key, secret_key, partner_name="TVTBookShop"):
        self.partner_code = partner_code
        self.access_key = access_key
        self.secret_key = secret_key
        self.partner_name = partner_name
        # Sandbox endpoint (change to https://api.momo.vn for production)
        self.endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
        self.check_endpoint = "https://test-payment.momo.vn/v2/gateway/api/query"
    def create_payment(self, order_id, amount, order_info, customer_name, customer_phone, return_url, notify_url):
        """
        Tạo request thanh toán Momo
        
        Args:
            order_id: ID đơn hàng
            amount: Số tiền (VND)
            order_info: Thông tin đơn hàng
            customer_name: Tên khách hàng
            customer_phone: SĐT khách hàng
            return_url: URL return sau khi thanh toán
            notify_url: URL nhận webhook từ Momo
        
        Returns:
            dict: Response từ Momo hoặc lỗi
        """
        
        request_id = str(order_id)
        extra_data = "bookshop"
        
        # Tạo raw signature theo đúng format
        raw_signature = f"accessKey={self.access_key}&amount={amount}&extraData={extra_data}&ipnUrl={notify_url}&orderId={request_id}&orderInfo={order_info}&partnerCode={self.partner_code}&redirectUrl={return_url}&requestId={request_id}&requestType=captureWallet"
        
        print(f"🔐 Raw Signature để hash: {raw_signature}")
        
        # Tạo signature bằng HMAC SHA256
        signature = hmac.new(
            self.secret_key.encode(),
            raw_signature.encode(),
            hashlib.sha256
        ).hexdigest()
        
        print(f"🔐 Signature: {signature}")
        
        # Prepare payload theo format đúng
        payload = {
            "partnerCode": self.partner_code,
            "accessKey": self.access_key,
            "requestId": request_id,
            "amount": str(amount),
            "orderId": order_id,
            "orderInfo": order_info,
            "redirectUrl": return_url,
            "ipnUrl": notify_url,
            "extraData": extra_data,
            "requestType": "captureWallet",
            "signature": signature,
            "lang": "vi"
        }
        
        print(f"� Payload gửi lên: {payload}")
        
        try:
            response = requests.post(self.endpoint, json=payload, timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def check_transaction(self, order_id):
        """
        Kiểm tra trạng thái giao dịch
        
        Args:
            order_id: ID đơn hàng
        
        Returns:
            dict: Trạng thái giao dịch
        """
        
        request_id = str(order_id)
        
        # Tạo raw signature
        raw_signature = f"accessKey={self.access_key}&orderId={request_id}&partnerCode={self.partner_code}&requestId={request_id}&secretKey={self.secret_key}"
        
        # Tạo signature
        signature = hmac.new(
            self.secret_key.encode(),
            raw_signature.encode(),
            hashlib.sha256
        ).hexdigest()
        
        payload = {
            "partnerCode": self.partner_code,
            "requestId": request_id,
            "orderId": request_id,
            "signature": signature,
            "lang": "vi"
        }
        
        try:
            response = requests.post(self.check_endpoint, json=payload, timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
