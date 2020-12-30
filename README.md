##Key Value based DataStore:

### Usage:

#### import the DataStore class
from dictdb import DataStore 

#### Create object
db = DataStore(save_directory='data')

#### Create entry (key=str, value=json, time=seconds)

db.create_entry(Key, Value, TimetoLive)

#####examples
db.create_entry('key1', json.dumps([1]), 100)

db.create_entry('key2', json.dumps([2]), 100)

db.create_entry('key3', json.dumps([3]), 100)

#### Delete entry
db.delete_entry('key2')

#### Read entry
db.read_entry('key1')

#### close and release file lock
db.close()

### Run tests

python testdatastore.py
