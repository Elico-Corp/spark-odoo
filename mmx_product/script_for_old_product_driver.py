import erppeek


SERVER = 'https://trunk.sparkmodel.com'
DADABASE = 'stable_mmx'
USER = 'admin'
PASSWORD = 'MMX3licoC0rp'

client = erppeek.Client(SERVER, DADABASE, USER, PASSWORD)
dd = client.model('product.driver').search([])
dd_id = client.model('product.driver').browse(dd)
for d in dd_id:
    d.write({'name': d.name})
