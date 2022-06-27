# -*- coding: utf-8 -*-
# from odoo import http


# class CarbizContract(http.Controller):
#     @http.route('/carbiz_contract/carbiz_contract/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/carbiz_contract/carbiz_contract/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('carbiz_contract.listing', {
#             'root': '/carbiz_contract/carbiz_contract',
#             'objects': http.request.env['carbiz_contract.carbiz_contract'].search([]),
#         })

#     @http.route('/carbiz_contract/carbiz_contract/objects/<model("carbiz_contract.carbiz_contract"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('carbiz_contract.object', {
#             'object': obj
#         })
