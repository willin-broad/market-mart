from django.urls import path
from . import views

urlpatterns = [
    path('make_mpesa_payment/<int:product_id>/', views.index, name='mpesa'),  # Form page

    path('stk_push/', views.stk_push, name='stk_push'),
    
    path('callback/', views.callback, name='callback'),
     path('waiting/<int:transaction_id>/', views.waiting_page, name='waiting_page'),
    path('check_status/<int:transaction_id>/', views.check_status, name='check_status'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('payment_failed/', views.payment_failed, name='payment_failed'),
    path('payment_cancelled/', views.payment_failed, name='payment_cancelled'),
    path('view_payments/', views.view_payments, name='view_payments'),
    path('account/<str:username>/', views.account_view, name='account'),
    path('api/seller/<int:seller_id>/account/', views.get_account, name='payment_status'),
  
]