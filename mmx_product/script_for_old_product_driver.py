import erppeek


client = erppeek.Client("http://localhost:7071", "odoo7_mmx_trunk_160523_test", "admin", "321")

dd = client.model('product.driver').search([])
dd_id = client.model('product.driver').browse(dd)
for d in dd_id:
    d.write({'name': d.name})
