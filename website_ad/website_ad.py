# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2015 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


import werkzeug

from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.addons.website.models.website import slug

import re

class ad_ad(models.Model):
    _name = "ad.ad"
    _description = "Adverticement"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'date_begin'

    name         = fields.Char(string='Title', index=True, readonly=True, states={'draft': [('readonly', False)]})
    description  = fields.Text(string='Description', index=True, readonly=True, states={'draft': [('readonly', False)]})
    state      = fields.Selection([('draft','Draft'),('published','Published'),('cancel','Cancelled'),('Done','done')], string='Status', index=True, readonly=True, default='draft', track_visibility='onchange', copy=False,
                    help=" * The 'Draft' status is used when the password is editable.\n"
                         " * The 'Sent' status is used when the password has been sent to the user.\n"
                         " * The'Cancelled'status is used when the password has been cancelled.\n")
    date_begin = fields.Datetime(string='Start Date', required=True,
        readonly=True, states={'draft': [('readonly', False)]})
    date_end = fields.Datetime(string='End Date', required=True,
        readonly=True, states={'draft': [('readonly', False)]})

    @api.one
    def button_draft(self):
        self.state = 'draft'
    @api.one
    def button_cancel(self):
        self.state = 'cancel'                
    @api.one
    def button_publish(self):
        self.state = 'published'
    @api.one
    def button_done(self):
        self.state = 'done'
        

class website_ad(http.Controller):
    @http.route(['/ad/<model("ad.ad"):ad>','/ad/new','/ad/<model("ad.ad"):ad>/delete','/ad/list'], type='json', auth="user", website=True)
    def order(self, ad=False, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        
        res_user = pool.get('res.users').browse(cr,uid,uid,context)

        if   not ad and re.search("list",request.httprequest.url) is not None:
            return pool.get('ad.ad').browse(cr,uid,uid,pool.get('res.users').search(cr,uid,[],context))
        elif not ad and re.search("new",request.httprequest.url) is not None:
            ad = pool.get('res.users').create(cr,uid,post)
            return True
        elif ad     and re.search("delete",request.httprequest.url) is not None:
                ad.unlink()
                return True
                
        return ad


