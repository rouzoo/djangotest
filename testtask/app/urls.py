from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('item/<int:item_id>/', views.detail, name='detail'),
    path('buy/<int:item_id>/', views.buy, name='buy'),
    path('config/', views.stripe_config),
    path('success/', views.SuccessView.as_view()),
    path('cancelled/', views.CancelledView.as_view()),
    path('webhook/', views.stripe_webhook),
    path('checkout/', views.checkout, name='checkout'),
]
