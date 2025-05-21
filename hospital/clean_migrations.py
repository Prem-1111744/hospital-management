import os 
DELETE_DB=True
project_root=os.getcwd()
print('cleaning django migrations files...\n')

for root, dirs ,files in os.walk(project_root):
    if 'migrations' in root:
        for file in files:
            if file !='__init__.py' and file.endswith('.py') or file.endswith('.pyc'):
                fullpath=os.path.join(root,file)
                os.remove(fullpath)
                print(f'deleted {fullpath}')

if DELETE_DB:
    db_path=os.path.join(project_root,'db.sqlite3')
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f'\n deleted database file {db_path}')

    else:
        print('\n no db.sqlite3 file found')

print('cleanup complete now run: ')