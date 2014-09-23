from csv import DictReader
import oerplib

"""
Put 1100 children into the database
"""

oerp = oerplib.OERP('localhost', protocol='xmlrpc', port=8069)

print(oerp.db.list())

user = oerp.login('admin', 'admin', 'fadder')
print(user.company_id.name)

"""
{'Status': '\xc3\x85pen', '': '', 'Name': 'Susso', 'Oppdatert skole juli 2012 fra Momodou': 'Talinding UBS', 'Mother': '', 'Father': '', 'Fadderbarn nr': '978', 'Sex': 'F', 'Forventet klasse 2012-13': '', 'Birth': '', 'Village': '', 'Fornavn': 'Isatou ', 'Avsluttet': '', 'Reg dato': '6/7/2011'}

"""

partner_attributes = ['name', 'phone', 'type', 'zip', 'city']
csv_columns = [('Fornavn', 'Name'), None, None, None, ('Village',)]
mapping = zip(csv_columns, partner_attributes)

partner_obj = oerp.get('res.partner')
for partner in partner_obj.browse(partner_obj.search([])):
    for attr in partner_attributes:
        print(partner[attr]),
    print



child = {'name' : 'Child1 Child1'}
#partner_obj.create(child)

csvfile = open('FadderBarn - Fadderbarn 14-15.csv')
csvfile.readline()



children = DictReader(csvfile)
for child in children:
    new_child = {}
    print "CHILD", child
    print mapping
    for src_attr, dst_attr in mapping:
        if src_attr == None:
            continue
        val = ' '.join( [child[x] for x in src_attr])
        print "VAL", val
        if not len(val.strip()):
            continue
        new_child[dst_attr] = val

    if new_child == {}:
        continue

    partner_obj.create(new_child)
