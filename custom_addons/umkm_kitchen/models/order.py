from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date

class UmkmOrder(models.Model):
    _name = 'umkm.order'
    _description = 'Pesanan Pelanggan'
    _inherit = ['mail.thread'] # for tracking & notification

    name = fields.Char(string='Nomor Order', required=True, copy=False, readonly=True, 
                       default=lambda self: 'New')
    customer_name = fields.Char(string='Nama Pelanggan')
    
    # relation to order lines
    order_line_ids = fields.One2many('umkm.order.line', 'order_id', string='Detail Pesanan')
    
    status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Dikonfirmasi'),
        ('done', 'Selesai'),
        ('canceled', 'Dibatalkan'),
    ], string='Status', default='draft', track_visibility='onchange') # track_visibility untuk Chatter

    total_price = fields.Float(string='Total Harga', compute='_compute_total_price', store=True)
    
    user_id = fields.Many2one(
        'res.users', 
        string='Dibuat Oleh', 
        default=lambda self: self.env.user, 
        readonly=True,
        track_visibility='onchange'
    )
    order_date = fields.Date(string='Tanggal Pesanan', default=date.today(), readonly=True)

    # sequence number
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                # generate sequence number (perlu dibuat sequence di data XML nanti)
                vals['name'] = self.env['ir.sequence'].next_by_code('umkm.order') or 'New'
        return super().create(vals_list)

    # compute total price
    @api.depends('order_line_ids.subtotal')
    def _compute_total_price(self):
        for order in self:
            order.total_price = sum(order.order_line_ids.mapped('subtotal'))

    # reduce stock on confirm
    def action_confirm(self):
        if self.status != 'draft':
            raise UserError("Pesanan sudah dikonfirmasi atau dibatalkan.")
            
        for line in self.order_line_ids:
            menu = line.menu_id
            
            if menu.stock < line.quantity:
                raise UserError(f"Stok untuk '{menu.name}' tidak cukup. Tersisa: {menu.stock} item.")
            
            menu.stock -= line.quantity
            
            if menu.stock < menu.low_stock_threshold:
                menu.message_post(
                    body=f"PERHATIAN! Stok '{menu.name}' berada di bawah batas **{menu.low_stock_threshold}** setelah order {self.name}. Stok saat ini: {menu.stock}.",
                    subject="Peringatan Stok Rendah"
                )
                
        self.status = 'confirmed'

    def action_done(self):
        self.status = 'done'

    def action_cancel(self):
        self.status = 'canceled'