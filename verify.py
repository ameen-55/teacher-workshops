import os
from app import create_app
from app.models import Workshop

# Force fresh database
db_path = os.path.join('instance', 'database.db')
if os.path.exists(db_path):
    os.remove(db_path)
    print(f'Deleted: {db_path}')

app = create_app()
with app.app_context():
    count = Workshop.query.count()
    print(f'Total workshops: {count}')
    for w in Workshop.query.all():
        print(f'- {w.title} ({w.instructor})')
    if count != 5:
        print('ERROR: Expected 5 workshops!')
    else:
        print('OK: Exactly 5 workshops.')