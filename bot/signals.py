from django.shortcuts import get_object_or_404
from .models import TakenSubscription
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver


@receiver(valid_ipn_received)
def payment_notification(sender, **kwargs):
    ipn = sender
    if ipn.payment_status == 'Completed':
        # payment was successful
        subscription = get_object_or_404(TakenSubscription, invoice=ipn.invoice)

        if subscription.subscription.price == ipn.mc_gross:
            # mark the order as paid
            subscription.paid = True
            subscription.save()
        else:
            print('Price: ', subscription.subscription.price)
            print('Paid: ', ipn.mc_gross)
    else:
        print(ipn.payment_status)