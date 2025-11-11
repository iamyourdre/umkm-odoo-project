from odoo import models, fields, api

class UmkmOrderLine(models.Model):
    _name = 'umkm.order.line'
    _description = 'Detail Baris Pesanan'

    # relation to order
    order_id = fields.Many2one('umkm.order', string='Pesanan', required=True, ondelete='cascade')
    
    menu_id = fields.Many2one('umkm.menu', string='Menu', required=True)
    quantity = fields.Integer(string='Jumlah', required=True, default=1)
    price_unit = fields.Float(string='Harga Satuan', required=True)
    
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit
            
    # get price on change
    @api.onchange('menu_id')
    def _onchange_menu_id(self):
        if self.menu_id:
            self.price_unit = self.menu_id.price