import sqlite3

conn = sqlite3.connect('aliaga.db')
cursor = conn.cursor()

print('=' * 60)
print('ALIAGA.DB - DATABASE OZETI')
print('=' * 60)

# Tablolar
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f'\nTABLOLAR: {[t[0] for t in tables]}')

# Her tablodaki kayit sayisi
for table in tables:
    cursor.execute(f'SELECT COUNT(*) FROM {table[0]}')
    count = cursor.fetchone()[0]
    print(f'  - {table[0]}: {count} kayit')

print('\n' + '=' * 60)
print('NOBETCI ECZANELER')
print('=' * 60)
cursor.execute('SELECT name, address, phone FROM pharmacy_duties')
for row in cursor.fetchall():
    print(f'  {row[0]}')
    print(f'    Adres: {row[1]}')
    print(f'    Tel: {row[2]}')

print('\n' + '=' * 60)
print('ACIL TELEFONLAR')
print('=' * 60)
cursor.execute("SELECT name, phone FROM institutions WHERE category='acil'")
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

print('\n' + '=' * 60)
print('KAMU KURULUSLARI (ilk 10)')
print('=' * 60)
cursor.execute("SELECT name, phone FROM institutions WHERE category='kamu' LIMIT 10")
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

print('\n' + '=' * 60)
print('BILGI TABANI KONULARI')
print('=' * 60)
cursor.execute('SELECT topic, title, LENGTH(content) as chars FROM knowledge_base')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[2]} karakter')

conn.close()
