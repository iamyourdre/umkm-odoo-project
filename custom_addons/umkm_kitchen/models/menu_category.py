from odoo import models, fields

class UmkmMenuCategory(models.Model):
    _name = 'umkm.menu.category'
    _description = 'Kategori Menu UMKM'

    name = fields.Char(string='Nama Kategori', required=True)
    
    menu_ids = fields.One2many(
        'umkm.menu',
        'category_id',
        string='Daftar Menu'
    )