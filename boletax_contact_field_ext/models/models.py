
# -*- coding: utf-8 -*-

from __future__ import print_function
from datetime import datetime
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError
import base64
import logging
import boto3
import json
_logger = logging.getLogger(__name__)
try:
    from OpenSSL import crypto
    type_ = crypto.FILETYPE_PEM
except ImportError:
    _logger.warning('Error en cargar crypto')


zero_values = {
    "filename": "",
    "key_file": False,
    "dec_pass": "",
    "not_before": False,
    "not_after": False,
    "status": "unverified",
    "final_date": False,
    "subject_title": "",
    "subject_c": "",
    "subject_serial_number": "",
    "subject_common_name": "",
    "subject_email_address": "",
    "issuer_country": "",
    "issuer_serial_number": "",
    "issuer_common_name": "",
    "issuer_email_address": "",
    "issuer_organization": "",
    "cert_serial_number": "",
    "cert_signature_algor": "",
    "cert_version": "",
    "cert_hash": "",
    "private_key_bits": "",
    "private_key_check": "",
    "private_key_type": "",
    "cacert": "",
    "cert": "",
}

class ContactExtension(models.Model):    
    _inherit ='res.partner'
    x_is_client = fields.Selection([('1','Si'),('0','No')],string='Cliente Principal')
    x_client_id = fields.Char(string='Número Cliente')
    x_apikey = fields.Char(string='Apikey')
    x_correo_login = fields.Char(string='Correo Login App')
    x_sucursal = fields.Char(string='Sucursal')
    dte_resolution_number = fields.Char(string='Número de Resolución Exenta')
    dte_resolution_date = fields.Date(string='Fecha de Resolución Exenta')
    dte_resolution_number_trial = fields.Char(string='Número de Resolución Exenta Certificación')
    dte_resolution_date_trial = fields.Date(string='Fecha de Resolución Exenta Certificación')
    
    legal_name = fields.Char(string='Representante Legal')
    legal_rut = fields.Char(string='Rut Representante Legal')
    legal_phone = fields.Char(string='Telefono Representante Legal')
    legal_email = fields.Char(string='Correo Representante Legal')
    x_comuna=fields.Char(string='Comuna')

    client_ref_id = fields.Many2one(
            'res.partner',
            string="Cliente",
        )
     
    #x_rut=fields.Char(string='Rut Comercio')
    #x_razon_social=fields.Char(string='Razón Social')
    #x_direccion=fields.Char(string='Dirección')
    
    @api.multi
    @api.onchange('client_ref_id')
    def update_customer(self):
        result = {}
        customer_id =  self.search(
                [
                    ('id','=', self.client_ref_id.id),
                ],
                limit=1,
            )
        self.x_client_id = customer_id[0].x_client_id
       

    def check_signature(self):
        for s in self:
            if not s.cert:
                s.status = 'unverified'
                continue
            expired = s.not_after < fields.Date.context_today(self)
            s.status = 'expired' if expired else 'valid'    

    def load_cert_pk12(self, filecontent):
        try:
            p12 = crypto.load_pkcs12(filecontent, self.dec_pass)
        except:
            raise UserError('Error al abrir la firma, clave incorrecta o el archivo no es compatible.')

        cert = p12.get_certificate()
        privky = p12.get_privatekey()
        cacert = p12.get_ca_certificates()
        issuer = cert.get_issuer()
        subject = cert.get_subject()

        self.not_before = datetime.strptime(cert.get_notBefore().decode("utf-8"), '%Y%m%d%H%M%SZ').date()
        self.not_after = datetime.strptime(cert.get_notAfter().decode("utf-8"), '%Y%m%d%H%M%SZ').date()

        # self.final_date =
        self.subject_c = subject.C
        self.subject_title = subject.title
        self.subject_common_name = subject.CN
        self.subject_serial_number = subject.serialNumber
        self.subject_email_address = subject.emailAddress

        self.issuer_country = issuer.C
        self.issuer_organization = issuer.O
        self.issuer_common_name = issuer.CN
        self.issuer_serial_number = issuer.serialNumber
        self.issuer_email_address = issuer.emailAddress

        self.cert_serial_number = cert.get_serial_number()
        self.cert_signature_algor = cert.get_signature_algorithm()
        self.cert_version = cert.get_version()
        self.cert_hash = cert.subject_name_hash()


        # data privada
        self.private_key_bits = privky.bits()
        self.private_key_check = privky.check()
        self.private_key_type = privky.type()
        # self.cacert = cacert

        certificate = p12.get_certificate()
        private_key = p12.get_privatekey()

        self.priv_key = crypto.dump_privatekey(type_, private_key)
        self.cert = crypto.dump_certificate(type_, certificate)

        #self.dec_pass = False

    filename = fields.Char(string='File Name')
    key_file = fields.Binary(
        string='Signature File', required=False, store=True,
        help='Upload the Signature File')
    dec_pass = fields.Char(string='Password')
    # vigencia y estado
    not_before = fields.Date(
        string='Not Before', help='Not Before this Date', readonly=True)
    not_after = fields.Date(
        string='Not After', help='Not After this Date', readonly=True)
    status = fields.Selection(
        [
                    ('unverified', 'Unverified'),
                    ('valid', 'Valid'),
                    ('expired', 'Expired')
        ],
        string='Status',
        compute='check_signature',
        help='''Draft: means it has not been checked yet.\nYou must press the\"check" button.''',
    )
    final_date = fields.Date(
        string='Last Date', help='Last Control Date', readonly=True)
    # sujeto
    subject_title = fields.Char(string='Subject Title', readonly=True)
    subject_c = fields.Char(string='Subject Country', readonly=True)
    subject_serial_number = fields.Char(
        string='Subject Serial Number')
    subject_common_name = fields.Char(
        string='Subject Common Name', readonly=True)
    subject_email_address = fields.Char(
        string='Subject Email Address', readonly=True)
    # emisor
    issuer_country = fields.Char(string='Issuer Country', readonly=True)
    issuer_serial_number = fields.Char(
        string='Issuer Serial Number', readonly=True)
    issuer_common_name = fields.Char(
        string='Issuer Common Name', readonly=True)
    issuer_email_address = fields.Char(
        string='Issuer Email Address', readonly=True)
    issuer_organization = fields.Char(
        string='Issuer Organization', readonly=True)
    # data del certificado
    cert_serial_number = fields.Char(string='Serial Number', readonly=True)
    cert_signature_algor = fields.Char(string='Signature Algorithm', readonly=True)
    cert_version = fields.Char(string='Version', readonly=True)
    cert_hash = fields.Char(string='Hash', readonly=True)
    # data privad, readonly=Truea
    private_key_bits = fields.Char(string='Private Key Bits', readonly=True)
    private_key_check = fields.Char(string='Private Key Check', readonly=True)
    private_key_type = fields.Char(string='Private Key Type', readonly=True)
    # cacert = fields.Char('CA Cert', readonly=True)
    cert = fields.Text(string='Certificate', readonly=True)
    priv_key = fields.Text(string='Private Key', readonly=True)
    authorized_users_ids = fields.Many2many('res.users',
       string='Authorized Users')

    @api.multi
    def action_clean1(self):
        self.write(zero_values)

    @api.multi
    def action_process(self):
        filecontent = base64.b64decode(self.key_file)
        self.load_cert_pk12(filecontent)

    @api.multi
    @api.model
    def _cron_procesar_cola(self):
        current_id = self.search([('id', '=', self.id)])
        
        sqs = boto3.client('sqs',
                       region_name='us-east-1',
                       aws_access_key_id='AKIATRZZJAQGO76WXPWR',
                       aws_secret_access_key='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')

        queue_url = 'https://sqs.us-east-1.amazonaws.com/244396393484/chl_test_odoo'

        # Send message to SQS queue
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageAttributes={
                'Title': {
                    'DataType': 'String',
                    'StringValue': 'Backend Notification'
                }
            },
            MessageBody={
                id:json.load(body)
            }
        )