from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from .models import Item
from django.conf import settings  # new
from django.http.response import JsonResponse  # new
from django.views.decorators.csrf import csrf_exempt  # new
from django.views.generic.base import TemplateView
import stripe
import os


def index(request):
    item_list = Item.objects.order_by('-name')
    template = loader.get_template('app/index.html')
    context = {
        'item_list': item_list,
    }
    return HttpResponse(template.render(context, request))


def detail(request, item_id):
    template = loader.get_template('app/item.html')
    item = Item.objects.get(pk=item_id)
    context = {
        'item': item,
    }
    return HttpResponse(template.render(context, request))


@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)


@csrf_exempt
def buy(request, item_id):
    item = Item.objects.get(pk=item_id)
    quantity = request.GET['itemCount']
    if request.method == 'GET':
        domain_url = os.environ.get("SERVER_HOST")
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            # Create new Checkout Session for the order
            # Other optional params include:
            # [billing_address_collection] - to display billing address details on the page
            # [customer] - if you have an existing Stripe Customer ID
            # [payment_intent_data] - capture the payment later
            # [customer_email] - prefill the email input in the form
            # For full details see https://stripe.com/docs /api/checkout/sessions/create

            # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + '/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + '/cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=[
                    {
                        'name': item.name,
                        'description': item.description,
                        'quantity': quantity,
                        'currency': 'rub',
                        'amount': item.price * 100,
                    },

                ],
                allow_promotion_codes=True,
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})


@csrf_exempt
def checkout(request):
    import json
    post_data = json.loads(request.body.decode('UTF-8'))
    cart = post_data['cart']
    cartItems = []

    for i in range(len(cart)):
        el = Item.objects.get(pk=cart[i]['item_id'])
        cartItems.append({
            'name': el.name,
            'description': el.description,
            'quantity': cart[i]['quantity'],
            'currency': 'rub',
            'amount': el.price * 100,
        })

    domain_url = os.environ.get("SERVER_HOST")
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        # Create new Checkout Session for the order
        # Other optional params include:
        # [billing_address_collection] - to display billing address details on the page
        # [customer] - if you have an existing Stripe Customer ID
        # [payment_intent_data] - capture the payment later
        # [customer_email] - prefill the email input in the form
        # For full details see https://stripe.com/docs /api/checkout/sessions/create

        # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
        checkout_session = stripe.checkout.Session.create(
            success_url=domain_url + '/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=domain_url + '/cancelled/',
            payment_method_types=['card'],
            mode='payment',
            line_items=cartItems,
            allow_promotion_codes=True,
        )
        return JsonResponse({'sessionId': checkout_session['id']})
    except Exception as e:
        return JsonResponse({'error': str(e)})


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        print("Payment was successful.")
        # TODO: run some custom code here

    return HttpResponse(status=200)


class SuccessView(TemplateView):
    template_name = 'app/success.html'


class CancelledView(TemplateView):
    template_name = 'app/cancelled.html'
