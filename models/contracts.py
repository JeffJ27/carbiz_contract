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
    balance = fields.Float('Balance')
    days = fields.Integer('Amount in Figures')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default="draft", string="State")


    def start_contract(self):
        for rec in self:
            rec.state = 'running'

    def cancel_contract(self):
        for rec in self:
            rec.state = 'cancelled'

    def auto_complete_contract(self):
        for rec in self:
            contract_records = self.env['contracts'].search([])
            for data in contract_records:
                if data.state == 'running':
                    data.state = 'completed'

    @api.onchange('amount','down_payment')
    def calc_balance(self):
        for rec in self:
            if rec.down_payment != 0.0:
                rec.balance = rec.amount - rec.down_payment
