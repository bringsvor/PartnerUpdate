#!/usr/bin/env python
#-.- encoding: utf-8 -.-


import sqlite3
import oerplib
from main import partner_columns, partner_attributes

def needs_curs():
    conn = sqlite3.connect('partners.db')
    curs = conn.cursor()

    try:
        curs.execute('select * from res_partner')
    except:
        print "Invalid database!"
        cols = ', '.join( [x[0] + ' ' + x[1] for x in partner_columns ])
        curs.execute('create table res_partner (%s)' % cols)
        print "COLS", cols
        conn.commit()

    return conn, curs

# TODO use the fast login mechanism of oerp
def connect_odoo(server, user, password):
    host, port = server.split(':')
    oerp = oerplib.OERP(host, protocol='xmlrpc', port=int(port))
    # TODO DB!
    user = oerp.login(user, password, 'barn')
    return oerp, user

def get_partners_from_db():
    partnerdata = {}
    conn, curs = needs_curs()
    res = curs.execute('select * from res_partner')
    cols = [x[0] for x in res.description]
    for ch in res:
        zz = zip(cols, ch)
        zzz = {}
        for a,b in zz:
            zzz[a] = b
        print "GET_FROM_DB", zz
        partnerdata[zzz['name']] = zzz
    return partnerdata


def fetch_partners(server, user, password):
    conn, curs = needs_curs()

    print "FETCH PARTNERS", conn, curs
    curs.execute('delete from res_partner')
    oerp, user = connect_odoo(server, user, password)
    partner_obj = oerp.get('res.partner')
    srch = partner_obj.search([])
    for child in partner_obj.read(srch, partner_attributes): # TODO filter
        d = []
        fields = []
        for field in partner_attributes:
            if child[field]:
                print "CHILD TYPE", type(child[field])
                if type(child[field]) is str or type(child[field]) is unicode:
                    d.append("'%s'" % child[field])
                else:
                    d.append(child[field])
                fields.append(field)

        q = 'insert into res_partner (%s) values (%s)' % (','.join(fields), ','.join(d))
        print "QUERY", q
        curs.execute(q)

        print "QU", q
    conn.commit()

