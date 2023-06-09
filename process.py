import asyncio

import pandas as pd
import pymongo
from bson import ObjectId

from geocode import geocode
from tasks import CloudTask

mongo = pymongo.MongoClient(
    'mongodb+srv://jonathan:9VTFu2dV77EGGnVu@cluster4.uz1yi.mongodb.net/?retryWrites=true&w=majority')
db = mongo['p2p']['analysis']

task_manager = CloudTask()


def convert_keys_to_camel_case(dictionary):
    return {to_camel_case(key): value for key, value in dictionary.items()}


def to_camel_case(snake_case_string):
    components = snake_case_string.lower().split(' ')
    return components[0] + ''.join(x.title() for x in components[1:])


def generate_chunks(data_frame, chunk_size):
    num_chunks = len(data_frame) // chunk_size + 1
    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = (i + 1) * chunk_size
        yield data_frame[start_idx:end_idx]


def save_records(records):
    print('Saving {0} records to database '.format(len(records)))
    n_records = [convert_keys_to_camel_case(x) for x in records]
    # print(n_records)
    db.insert_many(n_records)


def read_excel():
    print('Reading excel file')
    df = pd.read_excel('data.xlsx')
    chunk_size = 100
    for chunk in generate_chunks(df, chunk_size):
        save_records(chunk.to_dict('records'))


def process_and_update(x):
    location = geocode(x['buyerAddress1'], str(x['zipCode']).zfill(5), x['adminLevel3'])
    result = db.update_one({'_id': ObjectId(x['_id'])}, {'$set': {'processed': True, **location}})
    print(location, result.matched_count, result.modified_count)
    return True


async def send_task(x):
    await task_manager.create_task('https://p2p-analysis-qndxoltwga-uc.a.run.app/', "/process",
                                   x)


async def send_task_shipment(x):
    await task_manager.create_task('https://p2p-analysis-qndxoltwga-uc.a.run.app/', "/belongs_to_p99",
                                   x)


async def process_entries():
    f = {'p99_processed': {'$exists': False}}
    to_process = db.find(f).limit(5000)
    to_mark = []

    for x in to_process:
        to_mark.append(x)

    if len(to_mark) > 0:
        payload = {
            '_id': {
                '$in': [ObjectId(z['_id']) for z in to_mark]
            }
        }
        update = {
            '$set': {
                'p99_processed': True
            }
        }
        result = db.update_many(payload, update)
        print(result.matched_count, result.modified_count)

        for y in to_mark:
            await send_task_shipment(y)
    return True


if __name__ == '__main__':
    asyncio.run(process_entries())
