'''
Basic script for all the odoo scripts with the following options:

-s (--server): the odoo server to connect.
-d: database
-u: user
-p: password
'''
import optparse
import erppeek

parser = optparse.OptionParser()
parser.add_option(
    '-s', '--server', default=None)
parser.add_option('-d', '--database', help='database')
parser.add_option('-u', '--user', default=None, help='username')
parser.add_option(
    '-p', '--password', default=None, help='password, or it will be \
    requested on login')

(args, domain) = parser.parse_args()


SERVER = args.server
DADABASE = args.database
USER = args.user
PASSWORD = args.password

print SERVER
print DADABASE
print USER
print PASSWORD

client = erppeek.Client(SERVER, DADABASE, USER, PASSWORD)

dd = client.model('product.driver').search([])
dd_id = client.model('product.driver').browse(dd)
for d in dd_id:
    d.write({'name': d.name})

xx = client.model('magento.attribute.option').search([('driver_id', '!=', False)])
xx_ids = client.model('magento.attribute.option').browse(xx)
for x in xx_ids:
    a = x.driver_id.name_get()[1]
    x.write({'value': a})
    print x.value

print "finished the script."