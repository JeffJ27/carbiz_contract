# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError, AccessError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import logging
import requests
import urllib3
_logger = logging.getLogger(__name__)


class SalesOrderModel(models.Model):
    _inherit = 'sale.order'

    contract_count = fields.Integer('Contract Count', compute='get_contract_count')

    def show_contracts(self):
        return{
            'name':'Contracts',
            'domain':[('sales_order','=', self.id)],
            'view_type':'form',
            'res_model':'contracts',
            'view_id':False,
            'view_mode':'tree,form',
            'type': 'ir.actions.act_window',
            'context': "{'create': False}"

        }

    def get_contract_count(self): 
        for rec in self:
            count = self.env['contracts'].search_count([('sales_order','=',rec.id)])
            rec.contract_count = count


    def action_confirm(self):
            res = super(SalesOrderModel, self).action_confirm()
            if self.partner_id:
                for rec in self.order_line:
                    if rec.product_id:
                        contract_vals = {
                            'file_no' : self.partner_id.id,
                            'customer' : self.partner_id.id,
                            # 'contract_start_date' : date.today(),
                            'sales_order': self.id,
                            'amount' : self.amount_total,
                            # 'billing_fee' : rec.price_unit,
                            # 'billing_currency' : rec.currency_id.id,
                        }
                        customer_contract = self.env['contracts'].create(contract_vals)

            return res

class AccountPayment(models.Model):
    _inherit = 'account.payment'
