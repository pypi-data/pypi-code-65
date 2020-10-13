# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from trytond.wizard import Wizard, StateTransition
from trytond.transaction import Transaction

__all__ = ['UpdateNowWizard']


class UpdateNowWizard(Wizard):
    'Update Rates Now'
    __name__ = 'currency_rate_import_ecb.updatewiz'
    
    start_state = 'updtrate'
    updtrate = StateTransition()

    def transition_updtrate(self):
        pool = Pool()
        Curr1 = Pool().get('currency.currency')
        context = Transaction().context

        c_lst = Curr1.browse(context['active_ids'])
        Curr1.update_rate_online(c_lst)
        return 'end'

# end UpdateNowWizard
