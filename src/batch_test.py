from multiprocessing import Process, Lock
from coppelia import simulate
from time import sleep

offset_time = 1.0

def process_batch(batch):
    lock = Lock()
    batch_list = []
    for item in batch:
        item["Lock"] = lock
        batch_list.append(create_process_item(item))

    for item in batch_list:
        item.start()
        sleep(offset_time)

    for item in batch_list:
        item.join()

def create_process_item(parameters):
    process = Process(target=simulate, args=(parameters))
    return process