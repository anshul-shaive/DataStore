import time
import random
from datastoreutils import *


class DataStore:
    def __init__(self, save_directory='data', save_file='data.json'):
        self.save_directory = save_directory
        self.save_file = save_file
        self.timetolivefile = os.path.join(self.save_directory, 'timetolive.json')
        self.filelock = False
        self.timetolivelock = False
        self.hash_val = hash(str(random.randint(1, 99999)))  # hash value to check if file is accessed by same object
        os.makedirs(save_directory, exist_ok=True)
        self.save_file = os.path.join(self.save_directory, self.save_file)
        self.val = file_in_use(self.save_file, self.hash_val)

    def perform_action_thread_safe(self, func, *args):
        self.filelock = True
        success, resp = func(*args)
        self.filelock = False
        return success, resp

    def close(self):
        file_in_use(self.save_file, 0, True)

    def create_entry(self, new_key, new_value, time_to_live):
        if self.val and file_in_use(self.save_file, self.hash_val):
            if len(new_key) > 32 or len(new_value.encode('utf-8')) > 2 ** 10:
                print('Key too long. Max size: 32')
                return
            try:
                new_value = json.loads(new_value)
            except:
                print("Error parsing request data")
                return

            while True:
                if self.filelock:
                    time.sleep(random.random())
                else:
                    success, resp = self.perform_action_thread_safe(add_entry_to_datastore,
                                                                    new_key, new_value, self.save_file)
                    if not success:
                        print(resp)
                        return
                    while True:
                        if time_to_live is None:
                            break
                        elif not self.timetolivelock:
                            self.timetolivelock = True
                            timetolivedict = read_timetolive(self.timetolivefile)
                            timetolivedict[new_key] = (int(time.time()), int(time_to_live))
                            write_timetolive(timetolivedict, self.timetolivefile)
                            self.timetolivelock = False
                            break
                        else:
                            time.sleep(random.random())
                    break
            print(resp)
            return
        print("File in use")
        return

    def read_entry(self, key):
        if self.val and file_in_use(self.save_file, self.hash_val):
            if len(key) > 32:
                print('Key too long. Max size: 32')
                return
            cur_time = time.time()
            while True:
                if self.filelock:
                    time.sleep(random.random())
                else:
                    while True:
                        if not self.timetolivelock:
                            self.timetolivelock = True

                            if intimetolive(key, self.timetolivefile):
                                if not isalive(key, cur_time, self.timetolivefile):
                                    self.timetolivelock = False
                                    print('Cannot read. Key has expired')
                                    return
                                self.timetolivelock = False
                            break
                        else:
                            time.sleep(random.random())
                    success, resp = self.perform_action_thread_safe(read_entry_from_datastore, key, self.save_file)
                    if not success:
                        print(resp)
                        return
                    break
            print(json.dumps(resp))
            return json.dumps(resp)
        print("File in use")
        return

    def delete_entry(self, key):
        if self.val and file_in_use(self.save_file, self.hash_val):
            if len(key) > 32:
                print('Key too long. Max size: 32')
                return
            cur_time = time.time()
            while True:
                if self.filelock:
                    time.sleep(random.random())
                else:
                    while True:
                        if not self.timetolivelock:
                            self.timetolivelock = True
                            if intimetolive(key, self.timetolivefile):
                                if not isalive(key, cur_time, self.timetolivefile):
                                    self.timetolivelock = False
                                    print('Cannot delete. Key has expired')
                                    return
                                self.timetolivelock = False
                            break
                        else:
                            time.sleep(random.random())
                    success, resp = delete_entry_from_datastore(key, self.save_file, self.timetolivefile)
                    if not success:
                        print(resp)
                        return
                    break
            print(resp)
            return
        print("File in use")
        return


# Example
db = DataStore()
db.create_entry('key1', json.dumps([1]), 100)
db.create_entry('key2', json.dumps([2]), 100)
db.create_entry('key3', json.dumps([3]), 100)

db.delete_entry('key2')
db.read_entry('key1')

db.close()
