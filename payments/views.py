import requests
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseForbidden, JsonResponse

from marketplace.models import Product
from .models import Seller_Account, Transaction
import base64
from datetime import datetime
import json
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


from django.core.paginator import Paginator
import logging

logger = logging.getLogger(__name__)

class MpesaPassword:
    @staticmethod
    def generate_security_credential():
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
       
        business_short_code = '174379'  
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'  
        data_to_encode = business_short_code + passkey + timestamp
        online_password = base64.b64encode(data_to_encode.encode()).decode('utf-8')

        return online_password

CONSUMER_KEY = 'TVVmg2jP12SoHiiTs1Y1Ha0KMcUZCdXVxcG1VM5YrZPQc5CV'  
CONSUMER_SECRET = 'jMrqp2qvDyjsEwTCIYAddqwVGZPGPl3BDXwrInq446QzsETm0HkcJOXqUoEJ4OvX'  
SHORTCODE = '174379'  
PASSKEY = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'  
BASE_URL = 'https://sandbox.safaricom.co.ke'  

def generate_access_token():
    auth_url = f'{BASE_URL}/oauth/v1/generate?grant_type=client_credentials'
    response = requests.get(auth_url, auth=(CONSUMER_KEY, CONSUMER_SECRET))
    return response.json().get('access_token')

@login_required
def index(request, product_id):
    try:
        product = get_object_or_404(Product, id=product_id)
        return render(request, 'mpesa.html', {"product": product})
    except Exception as e:
        logger.error(f"Error fetching product with ID {product_id}: {e}")
        return render(request, 'error.html', {"error_message": "An error occurred."})


@csrf_exempt
def stk_push(request):
    if request.method == 'POST':
        try:
            seller_id = request.POST.get('seller')
            phone = request.POST.get('phone')
            amount = request.POST.get('amount')
            name = request.POST.get('name')
            email = request.POST.get('email')
            product_id = request.POST.get('product')

            # Fetch the Seller instance (not User) based on the username
            seller = Seller_Account.objects.get(id=seller_id) 
            product = Product.objects.get(id=product_id)
            print(seller)

            transaction = Transaction.objects.create(
                seller=seller,  
                product=product,
                phone_number=phone,
                amount=amount,
                status="Pending",
                description="Awaiting callback",
                name=name,
                email=email,
            )

            access_token = generate_access_token()
            stk_url = f'{BASE_URL}/mpesa/stkpush/v1/processrequest'
            headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = base64.b64encode(f'{SHORTCODE}{PASSKEY}{timestamp}'.encode()).decode()

            payload = {
                "BusinessShortCode": SHORTCODE,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": amount,
                "PartyA": phone,
                "PartyB": SHORTCODE,
                "PhoneNumber": phone,
                "CallBackURL": "https://3985-105-163-0-87.ngrok-free.app/callback/",
                "AccountReference": f"Transaction_{transaction.id}",
                "TransactionDesc": "Payment for services"
            }

            response = requests.post(stk_url, json=payload, headers=headers)
            response.raise_for_status()

            response_data = response.json()
            transaction.transaction_id = response_data.get('CheckoutRequestID')
            transaction.description = response_data.get('ResponseDescription', 'No description')
            transaction.save()

            return redirect('waiting_page', transaction_id=transaction.id)

        except Exception as e:
            print(f"Error during STK push: {e}")
            return JsonResponse({"error": "Payment request failed"}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)



@csrf_exempt
def callback(request):
    print("callback")
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Received callback data:", data)

            stk_callback = data.get('Body', {}).get('stkCallback', {})
            result_code = stk_callback.get('ResultCode', None)
            result_desc = stk_callback.get('ResultDesc', '')  
            transaction_id = stk_callback.get('CheckoutRequestID', None)

            if transaction_id:
                transaction = Transaction.objects.filter(transaction_id=transaction_id).first()
                if transaction:
                    if result_code == 0:  # Payment Success
                        callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                        receipt_number = next((item.get('Value') for item in callback_metadata if item.get('Name') == 'MpesaReceiptNumber'), None)
                        amount = next((item.get('Value') for item in callback_metadata if item.get('Name') == 'Amount'), None)
                        transaction_date_str = next((item.get('Value') for item in callback_metadata if item.get('Name') == 'TransactionDate'), None)

                        # Parse the transaction date
                        transaction_date = None
                        if transaction_date_str:
                            transaction_date = datetime.strptime(str(transaction_date_str), "%Y%m%d%H%M%S")

                        # Update the transaction details
                        transaction.mpesa_receipt_number = receipt_number
                        transaction.transaction_date = transaction_date
                        transaction.amount = amount
                        transaction.status = "Success"
                        transaction.description = "Payment successful"
                        transaction.save()

                        # Update seller balance
                        transaction.update_balance()

                        print(f"Transaction {transaction_id} updated as successful.")

                        #
                        
                    elif result_code == 1:  # Payment failed
                        transaction.status = "Failed"
                        transaction.description = result_desc
                        transaction.save()
                        print(f"Transaction {transaction_id} marked as failed: {result_desc}")

                    elif result_code == 1032:  # Payment cancelled
                        transaction.status = "Cancelled"
                        transaction.description = "Transaction cancelled by the user"
                        transaction.save()                        
                        
                        print(f"Transaction {transaction_id} marked as cancelled.")

                    else:
                        transaction.status = "Failed"
                        transaction.description = "Transaction Failed"
                        transaction.save()                        
                        
                        print(f"Transaction {transaction_id} Failed.")
                           

            return JsonResponse({"message": "Callback received and processed"}, status=200)

        except Exception as e:
            print(f"Error processing callback: {e}")
            return JsonResponse({"error": "An error occurred while processing the callback"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)


@login_required
def waiting_page(request, transaction_id):
    transaction = Transaction.objects.get(id=transaction_id)
    return render(request, 'waiting.html', {'transaction_id': transaction_id})

@login_required
def check_status(request, transaction_id):
    transaction = Transaction.objects.filter(id=transaction_id).first()

    if not transaction:
        print(f"trans {transaction.status}")
        return JsonResponse({"status": "Failed", "message": "Transaction not found"}, status=404)

    if transaction.status == "Success":
        return JsonResponse({"status": "Success", "message": "Payment Successful"})
    elif transaction.status == "Failed":
        return JsonResponse({"status": "Failed", "message": "Payment Failed"})
    elif transaction.status == "Cancelled":
        return JsonResponse({"status": "Cancelled", "message": "Transaction was cancelled by the user"})
    else:
        return JsonResponse({"status": "Unknown", "message": "Transaction is still being processed or status is unknown"})

@login_required
def payment_success(request):
    return render(request, 'payment_success.html')

@login_required
def payment_failed(request):
    return render(request, 'payment_failed.html')

@login_required
def payment_cancelled(request):
    return render(request, 'payment_cancelled.html')

@login_required
def view_payments(request):
    search_query = request.GET.get('q', '')
    page_number = request.GET.get('page', 1)

   
    payments = Transaction.objects.filter(
        phone_number__icontains=search_query
    ) | Transaction.objects.filter(
        transaction_id__icontains=search_query
    ) | Transaction.objects.filter(
        name__icontains=search_query
    ) | Transaction.objects.filter(
        mpesa_receipt_number__icontains=search_query
    )

    paginator = Paginator(payments, 10)  
    page_obj = paginator.get_page(page_number)

   
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  
        payments_list = [
            {
                'id': payment.id,
                'transaction_id': payment.transaction_id,
                'name': payment.name,
                'phone_number': payment.phone_number,
                'amount': str(payment.amount),
                'status': payment.status,
                'mpesa_receipt_number': payment.mpesa_receipt_number,
                'transaction_date': payment.transaction_date.strftime("%Y-%m-%d %H:%M:%S") if payment.transaction_date else "N/A",
                'email': payment.email,
            }
            for payment in page_obj
        ]
        return JsonResponse({
            'payments': payments_list,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
        })

    return render(request, 'view_payments.html', {'page_obj': page_obj})



def get_account(request, seller_id):
    # Check if the seller exists
    seller = get_object_or_404(User, id=seller_id)
    
    # Fetch the seller's account details
    account = get_object_or_404(Seller_Account, user=seller)
    
    # Fetch the seller's transactions
    transactions = Transaction.objects.filter(seller=account).order_by('-date_created')[:10]  # Last 10 transactions

    # Prepare data to return as JSON
    data = {
        "name": seller.username,
        "email": seller.email,
        "balance": account.balance,
        "transactions": [
            {
                "date_created": transaction.date_created,
                "buyer": transaction.name,
                "amount": transaction.amount,
                "status": transaction.status,
            }
            for transaction in transactions
        ],
    }

    return JsonResponse(data, safe=False)


@login_required
def account_view(request, username):
    user = get_object_or_404(User, username=username)
    if request.user != user:
        return HttpResponseForbidden("You are not authorized to view this page.")
    return render(request, 'account.html', {'user': user})


