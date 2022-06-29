# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, AccessError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import logging
import requests
import urllib3
_logger = logging.getLogger(__name__)

class RentContracts(models.Model):
    _name = 'contracts'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']

    chassis_no = fields.Char('Chassis No')
    model = fields.Many2one('fleet.vehicle.model','Model')
    reg_no = fields.Many2one('fleet.vehicle','Reg No')
    color = fields.Char('Colour')
    file_no = fields.Char('File No')

    customer = fields.Many2one('res.partner', string="Purchaser")
    address = fields.Char('Address')
    phone = fields.Char('Phone')
    po_box = fields.Char('P.O.Box')
    sales_order = fields.Many2one('sale.order', string="Sales Order")
    product_id = fields.Many2one('product.product', string="Product")
    amount = fields.Float('Amount in Figures')
    amount_words = fields.Float('Amount in Words', tracking=True)
    down_payment = fields.Float('Down Payment')
    balance = fields.Float('Balance Before Delivery')
    days_balance = fields.Integer('Days to clear balance')
    balance_installment = fields.Float('Installment Balance')
    days_installment = fields.Integer('Days to clear installments')
    days = fields.Integer('Days to clear installment')
    date_delivery = fields.Date('Final Day Delivery')
    date_installment = fields.Date('Final Day Installment')
    no_install = fields.Integer('No of Installments')
    installment_lines = fields.One2many('install.line', 'contract_id', string='Installments')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default="draft", string="State")

    @api.onchange('days_balance')
    def get_date_first_balance(self):
        for rec in self:
            if rec.days_balance:
                rec.date_delivery = date.today() + relativedelta(days=rec.days_balance)

    @api.onchange('days_installment')
    def get_date_last_balance(self):
        for rec in self:
            if rec.days_installment:
                rec.date_installment = date.today() + relativedelta(days=rec.days_installment)


    def start_contract(self):
        for rec in self:
            rec.state = 'running'
            rec.compute_installments()

    def cancel_contract(self):
        for rec in self:
            rec.state = 'cancelled'

    def auto_complete_contract(self):
        for rec in self:
            contract_records = self.env['contracts'].search([])
            for data in contract_records:
                if data.state == 'running':
                    data.state = 'completed'

    @api.onchange('amount','down_payment','balance')
    def calc_balance(self):
        for rec in self:
            if rec.down_payment != 0.0:
                rec.balance_installment = rec.amount - (rec.down_payment + rec.balance)


    def compute_installments(self):
        count = 0
        date_pay = date.today()
        for rec in self:
            rec.installment_lines.unlink()
            for i in range(1, rec.no_install + 1, 1):
                count += 1
                date_pay = date_pay + relativedelta(days=int(rec.days_installment/rec.no_install))
                self.env['install.line'].create({
                        'amount' : rec.balance_installment/rec.no_install,
                        'payment_date' : date_pay,
                        'status': 'not_paid',
                        'contract_id': rec.id,
                })

class LineInstallments(models.Model):
    _name = "install.line"
    _description = "Installments"

    contract_id = fields.Many2one('contracts', 'Contract ID')
    amount = fields.Float(string="Amount")
    payment_date = fields.Date('Payment Date')
    status = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('cleared', 'Cleared'),
    ], string='Status')

    paid = fields.Boolean(string='Paid',
                          help="True if this rent is paid by tenant")
    payment_id = fields.Many2one('account.payment', string='Invoice')
    payment = fields.Boolean(string='Is Payment?')

    invoice_name = fields.Char('Invoice Name')

    def create_payment(self):
        obj = self.env['account.payment']
        vals = {
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.contract_id.customer.id,
            'journal_id': self.payment_type_id.id,
            'amount': self.amount,
            'ref': self.file_no,
            'state': 'draft',
        }
        self.write({'status': 'cleared'})
        res = obj.create(vals)
        return res

    def open_payment(self):
        """Method Open Invoice."""
        context = dict(self._context or {})
        wiz_form_id = self.env.ref('account.view_account_payment_form').id
        return {
            'view_type': 'form',
            'view_id': wiz_form_id,
            'view_mode': 'form',
            'res_model': 'account.payment',
            'res_id': self.payment_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': context,
        }