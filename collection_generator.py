#!/usr/bin/python3


import sqlite3
import argparse

def total_rows(cursor, table_name, print_out=False):
    """ Returns the total number of rows in the database """
    cursor.execute('SELECT COUNT(*) FROM {}'.format(table_name))
    count = cursor.fetchall()
    if print_out:
        print('Total rows: {}'.format(count[0][0]))
    return count[0][0]

def table_col_info(cursor, table_name, print_out=False):
    """ Returns a list of tuples with column informations:
        (id, name, type, notnull, default_value, primary_key)
    """
    cursor.execute('PRAGMA TABLE_INFO({})'.format(table_name))
    info = cursor.fetchall()

    if print_out:
        print("Column Info:")
        print("ID, Name, Type, NotNull, DefaultVal, PrimaryKey")
        for col in info:
            print(col)
    return info

def values_in_col(cursor, table_name, print_out=False):
    """ Returns a dictionary with columns as keys and the number of not-null
        entries as associated values.
    """
    cursor.execute('PRAGMA TABLE_INFO({})'.format(table_name))
    info = cursor.fetchall()
    col_dict = dict()
    for col in info:
        col_dict[col[1]] = 0
    for col in col_dict:
        cursor.execute('SELECT ({0}) FROM {1} WHERE {0} IS NOT NULL'.format(col, table_name))
        # In my case this approach resulted in a better performance than using COUNT
        number_rows = len(cursor.fetchall())
        col_dict[col] = number_rows
    if print_out:
        print("Number of entries per column:")
        for i in col_dict.items():
            print('{}: {}'.format(i[0], i[1]))
    return col_dict

def rows(cursor, table_name, print_out=False):
    if(print_out):
        print("Rows of table '%s':" % table_name)
    cursor.execute('SELECT * FROM %s' %table_name)
    rows = cursor.fetchall()
    if(print_out and len(rows) == 0):
        print("<empty>")
    else:
        for row in rows:
            if(print_out):
                print(row)
    return rows

def do_nothing(*args):
    pass


def connect_databases(device):
    import os
    try:
        dbfile_books = os.path.join(device, 'Sony_Reader','database','books.db')
        conn_books = sqlite3.connect(dbfile_books)
    except sqlite3.OperationalError as err:
        print(err)
        print(dbfile_books)
        exit(1)
        
    
    try:
        dbfile_notepads = os.path.join(device, 'Sony_Reader','database','notepads.db')
        conn_notepads = sqlite3.connect(dbfile_notepads)
    except sqlite3.OperationalError as err:
        print(err)
        print(dbfile_notepads)
        exit(1)

    return conn_books, conn_notepads

def print_tables(device):
    conn_books, conn_notepads = connect_databases(device)
    c_b = conn_books.cursor()
    c_np = conn_books.cursor()
    
    c = c_b
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    for table in tables:
        print("Table: " + str(table))
        table_name = table[0]
        
        # Retrieve column information
        # Every column will be represented by a tuple with the following attributes:
        # (id, name, type, notnull, default_value, primary_key)
        #c.execute('PRAGMA TABLE_INFO({})'.format(table_name))
        table_col_info(c, table_name, True)
        values_in_col(c, table_name, True)
        total_rows(c, table_name, True)
        rows(c, table_name, True)
        
        print()
    
    conn_books.close()
    conn_notepads.close()

def del_collections(device):
    conn_books, conn_notepads = connect_databases(device)
    c_b = conn_books.cursor()
    c_np = conn_books.cursor()

    c = c_b
    for table_name in ['collection', 'collections']:
        result = c.execute("DELETE FROM %s" % table_name)
        print("+"*40)
        print("I just deleted", result.rowcount, "rows from ", table_name )
        print("+"*40)
        table_col_info(c, table_name, True)
        values_in_col(c, table_name, True)
        total_rows(c, table_name, True)
        rows(c, table_name, True)
        print()

    conn_books.close()
    conn_notepads.close()


def gen_collections(device):
    import re
    import os
    
    conn_books, conn_notepads = connect_databases(device)
    c_b = conn_books.cursor()
    c_np = conn_books.cursor()

    c = c_b


    rel_path_prog = re.compile(r"^"+os.path.join("Sony_Reader","media","books")+os.path.sep+"(.*)$")
    
    for row in c.execute('SELECT * FROM books ORDER BY title').fetchall():
        print(row)
        try:
            book_id = row[0]
            filepath = row[12].strip()
            rel_path = rel_path_prog.match(filepath).group(1)
            rel_path = os.path.dirname(rel_path).strip()
            print("book %d at %s, collection '%s'" % (book_id, filepath, rel_path))
        except Exception as err:
            print(err)
            print(filepath)
            print()
            continue
        
        if(rel_path != ''):
            print("put this content into a collection...")
            
            #check if collection already exists
            collection_name = rel_path
            result = c.execute("SELECT _id FROM collection WHERE title=?", (collection_name,)).fetchone()
            if(result is None):
                #add a new collection
                result = c.execute("INSERT INTO collection(title, source_id) values (?, ?)", (collection_name, 1))

                # obtain the id of the new collection
                result = c.execute("SELECT _id FROM collection WHERE title=?", (collection_name,)).fetchone()
                collection_id = result[0]
            else:
                collection_id = result[0]
            
            print("belongs to collection %d" % collection_id)
            
            #check if book is already in collections table
            result = c.execute("SELECT _id FROM collections WHERE content_id=? AND collection_id=?", (book_id,collection_id)).fetchone()
            if(result is None):
                result = c.execute("INSERT INTO collections(collection_id, content_id) values (?, ?)", (collection_id, book_id))
            else:
                result = c.execute("UPDATE collections SET collection_id=? WHERE content_id=?", (collection_id, book_id))
        print()

 
    #print the new table
    for table_name in ['collection', 'collections']:
        table_col_info(c, table_name, True)
        values_in_col(c, table_name, True)
        total_rows(c, table_name, True)
        rows(c, table_name, True)
        print()
        
    # Save (commit) the changes
    conn_books.commit()
    
    conn_books.close()
    conn_notepads.close()

    

if __name__ == '__main__':

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description=
"""Display and manipulate the SQlite databases on the Sony PRS-T2 Ebook Reader.
Maybe this script works also for other Sony Ebook Readers, but the author does
not have access to any and cannot test that.""",
                                     epilog=
"""This program is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
    )
    parser.add_argument('--print', dest='print_func', action='store_const',
                        const=print_tables, default=do_nothing,
                        help='print the content of all database tables on the screen')
    parser.add_argument('--delete-collections', dest='del_collections_func', action='store_const',
                        const=del_collections, default=do_nothing,
                        help='delete all collections on the reader')
    parser.add_argument('--generate-collections', dest='gen_collections_func', action='store_const',
                        const=gen_collections, default=do_nothing,
                        help="generate collections according to the folder structure\n below the "+os.path.join("Sony_Reader","books")+" folder on the reader")
    parser.add_argument('device', action='store', nargs='?',
                        default=os.path.curdir,
                        help='The mount point of the PRS-T2. (default '+os.path.curdir+' )')
    args = parser.parse_args()
    args_vars = vars(parser.parse_args())
    print(args_vars)
    if(args_vars['print_func'] == do_nothing and
       args_vars['gen_collections_func'] == do_nothing and
       args_vars['del_collections_func'] == do_nothing):
        parser.error('No arguments provided.')

    args.print_func(args.device)
    args.del_collections_func(args.device)
    args.gen_collections_func(args.device)
