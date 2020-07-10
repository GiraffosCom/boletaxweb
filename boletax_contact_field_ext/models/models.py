
# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ContactExtension(models.Model):    
    _inherit ='res.partner'
    

    x_apikey=fields.Char(string='Apikey')
    x_correo_login=fields.Char(string='Correo Login App')
    x_sucursal=fields.Char(string='Sucursal')
    #x_rut=fields.Char(string='Rut Comercio')
    #x_razon_social=fields.Char(string='Razón Social')
    #x_direccion=fields.Char(string='Dirección')
    #x_comuna=fields.Char(string='Comuna')