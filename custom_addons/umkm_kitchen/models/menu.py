from odoo import models, fields, api
from odoo.exceptions import ValidationError

class UmkmMenu(models.Model):
    _name = 'umkm.menu'
    _description = 'Menu dan Stok Produk'
    _inherit = ['mail.thread']

    name = fields.Char(string='Nama Menu', required=True)
    category_id = fields.Many2one('umkm.menu.category', string='Kategori')
    price = fields.Float(string='Harga Jual', required=True, default=0.0)
    
    # stock management fields
    stock = fields.Integer(string='Stok Saat Ini', default=0)
    low_stock_threshold = fields.Integer(string='Batas Stok Rendah', default=10)
    is_available = fields.Boolean(string='Tersedia Dijual', default=True)

    # low stock notification
    stock_status = fields.Char(
        string='Status Stok',
        compute='_compute_stock_status',
        store=True
    )
    
    @api.depends('stock', 'low_stock_threshold')
    def _compute_stock_status(self):
        for record in self:
            if record.stock <= 0:
                record.stock_status = 'Stok Habis'
            elif record.stock < record.low_stock_threshold:
                record.stock_status = 'Stok Rendah'
            else:
                record.stock_status = 'Cukup'

    # reject negative values
    @api.constrains('price', 'stock', 'low_stock_threshold')
    def _check_non_negative_values(self):
        for record in self:
            if record.price < 0 or record.stock < 0 or record.low_stock_threshold < 0:
                raise ValidationError("Harga, Stok, dan Batas Stok tidak boleh negatif.")

    # menu name must be unique
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Nama Menu harus unik!'),
    ]