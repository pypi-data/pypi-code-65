from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.conf import settings
from psu_base.classes.Log import Log
from psu_base.services import utility_service, error_service, auth_service, message_service
from psu_base.decorators import require_authority, require_authentication
from psu_cashnet.models.transaction import Transaction
from psu_cashnet.services import transaction_service
from django.core.paginator import Paginator
from django.db.models import Q
import re
from datetime import datetime

log = Log()


# Cashnet Error Page
# (template can be overridden at the app level)
def cn_error_page(request):
    auth_service.audit_event("ERROR_PAGE", comments=f"Customer directed to Cashnet error page")
    return render(
        request, 'cn_error.html', {}
    )


# Recording of the Cashnet response should NOT require authentication
def cn_record_response(request):
    """Record the response from cashnet"""
    tx = transaction_service.record_cashnet_response(request)
    if tx and tx.is_recorded():
        return redirect('cashnet:validation', tx.id)
    else:
        return redirect('cashnet:error')


@require_authentication()
def cn_validate_response(request, tx_id):
    """
    Handle a response from Cashnet
    """
    tx = transaction_service.confirm_cashnet_response(tx_id)
    log.info(f"Confirmed response: {tx}")

    # If valid transaction (success or failure)
    if tx and tx.was_processed():
        transaction_service.set_processed_transaction(tx)
        if tx.was_successful():
            return redirect(tx.success_url)
        else:
            return redirect(tx.failure_url)

    # Otherwise, send to error page
    else:
        redirect('cashnet:error')


@require_authority(['cashnet'])
def cn_admin_update_tx(request, tx_id, status):

    tx = get_object_or_404(Transaction, pk=tx_id)
    status_code = status.strip()[:1].upper() if status else None

    # Since this action will fire off post-payment processing, user must be proxying the customer
    auth = auth_service.get_auth_object()
    current_user = auth.get_user()
    proxied_user = auth.proxied_user if auth.is_proxying() else None

    # User may not update their own transaction
    if tx.customer_username == current_user.username:
        message_service.post_error("You may not update your own transaction status")
        return redirect('cashnet:transaction_detail', tx.id)

    elif (not proxied_user) or proxied_user.username != tx.customer_username:
        message_service.post_error("You must be proxying the customer when you update their transaction status.")
        return redirect('cashnet:transaction_detail', tx.id)

    if tx and status_code in ['S', 'F']:
        auth_service.audit_event(
            "UPDATE_CASHNET_STATUS", previous_value=tx.status_code, new_value=status_code, comments=f"{tx}"
        )

        tx.status_code = status_code
        tx.admin_updated = current_user.username
        tx.admin_updated_date = datetime.now()
        tx.save()
        transaction_service.set_processed_transaction(tx)

        if tx.was_successful():
            return redirect(tx.success_url)
        else:
            return redirect(tx.failure_url)

    message_service.post_error("Invalid transaction or status was provided.")
    return redirect('cashnet:transaction_detail', tx.id)


@require_authority(['cashnet'])
def cn_transaction_index(request):
    """
    Show all transactions
    """
    log.trace()

    # Start a query set
    transactions = Transaction.objects.all()

    # Get pagination sort and filter data
    sortby, page, kw = utility_service.pagination_sort_info(request, 'last_updated', 'desc', filter_name='keywords')

    if kw:
        for ww in kw.split():
            if re.match(r'^9\d{8}$', ww):
                transactions = transactions.filter(customer_psu_id=ww)
            elif re.match(r'^20[2-3]\d0[1-4]$', ww):
                transactions = transactions.filter(term_code=ww)
            elif ww.lower() in ['new', 'initiated', 'processing', 'success', 'failure', 'error']:
                transactions = transactions.filter(status_code=ww.upper()[:1])
            elif ':' in ww:
                log.debug(f"FILTER ::::::::::::::::::: {ww} has colon")
                pieces = ww.split(':')
                transactions = transactions.filter(reference_class__iexact=pieces[0])
                if len(pieces) > 1 and pieces[1]:
                    log.debug(f"FILTER ::::::::::::::::::: {ww} has id")
                    transactions = transactions.filter(reference_id=pieces[1])
            else:
                transactions = transactions.filter(
                    Q(customer_name__icontains=ww) |
                    Q(customer_username=ww)
                )

    transactions = transactions.order_by(sortby)

    # Reference object is made of two pieces and needs a secondary sort column
    if 'reference_id' in sortby:
        d = '-' if '-' in sortby else ''
        transactions = transactions.order_by(f'{d}reference_class')

    paginator = Paginator(transactions, 50)
    transactions = paginator.get_page(page)

    return render(
        request, 'transaction/cn_transaction_index.html',
        {'transactions': transactions, 'keywords': kw}
    )


@require_authority(['cashnet'])
def cn_transaction_detail(request, tx_id):
    """
    Show one transaction
    """
    log.trace()

    tx = get_object_or_404(Transaction, pk=tx_id)

    # If user has both cashnet and proxy authorities, they may update the status of transactions in Error status
    can_update = tx.status_can_be_updated() and auth_service.get_user().username != tx.customer_username
    can_proxy = auth_service.has_authority('proxy')
    is_proxied = auth_service.get_auth_object().proxied_user.username == tx.customer_username

    return render(
        request, 'transaction/cn_transaction_detail.html',
        {
            'tx': tx,
            'can_update': can_update,
            'can_proxy': can_proxy,
            'is_proxied': is_proxied,
        }
    )
