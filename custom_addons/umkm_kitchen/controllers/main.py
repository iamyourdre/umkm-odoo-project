from odoo import http
from odoo.http import request
import json

class UmkmApi(http.Controller):
    
    # /api/menu/list (GET)
    @http.route('/api/menu/list', type='json', auth='public', methods=['GET'], csrf=False)
    def menu_list(self):
        menus = request.env['umkm.menu'].sudo().search_read(
            domain=[('is_available', '=', True)],
            fields=['id', 'name', 'category_id', 'price', 'stock']
        )
        
        formatted_menus = []
        for menu in menus:
            category_name = menu['category_id'][1] if menu.get('category_id') else 'Uncategorized'
            menu['category_name'] = category_name
            del menu['category_id']
            formatted_menus.append(menu)
            
        return {
            'success': True,
            'menus': formatted_menus
        }

    # /api/order/create (POST)
    @http.route('/api/order/create', type='json', auth='public', methods=['POST'], csrf=False)
    def order_create(self):
        data = request.jsonrequest
        customer_name = data.get('customer_name')
        items = data.get('items')

        if not customer_name or not items:
            return {'success': False, 'message': 'Nama pelanggan dan item pesanan wajib diisi.'}

        order_lines = []
        
        for item in items:
            menu_id = item.get('menu_id')
            quantity = item.get('quantity')
            
            if not menu_id or not quantity or quantity <= 0:
                return {'success': False, 'message': 'Detail item tidak valid.'}
            
            menu = request.env['umkm.menu'].sudo().browse(menu_id)
            if not menu or not menu.is_available:
                return {'success': False, 'message': f"Menu ID {menu_id} tidak ditemukan atau tidak tersedia."}
                
            if menu.stock < quantity:
                return {'success': False, 'message': f"Stok '{menu.name}' tidak cukup. Tersisa: {menu.stock}."}
            
            order_lines.append((0, 0, {
                'menu_id': menu_id,
                'quantity': quantity,
                'price_unit': menu.price,
            }))

        # create order
        try:
            order_vals = {
                'customer_name': customer_name,
                'order_line_ids': order_lines,
                'user_id': request.env.user.id # created by Public/Guest user
            }
            
            # Using .sudo() to ensure public user can create order
            new_order = request.env['umkm.order'].sudo().create(order_vals)
            
            new_order.sudo().action_confirm()

            return {
                'success': True,
                'order_id': new_order.id,
                'order_number': new_order.name,
                'total_price': new_order.total_price,
                'message': 'Pesanan berhasil dibuat dan dikonfirmasi.'
            }
        
        except Exception as e:
            return {'success': False, 'message': str(e)}