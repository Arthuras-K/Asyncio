import asyncio
import datetime
from aiohttp import ClientSession
from more_itertools import chunked
from models import engine, Session, Base, SwapiPeople


CHUNK_SIZE = 3

async def get_people(session: ClientSession, people_id: int) -> dict:
    async with session.get(f'https://swapi.dev/api/people/{people_id}') as response:
        if response.status != 200:
            return []
        people_json = await response.json()
    result = {'id': people_id, 
            'birth_year': people_json['birth_year'],
            'eye_color': people_json['eye_color'],
            'films': people_json['films'],
            'gender': people_json['gender'],
            'hair_color': people_json['hair_color'],
            'height': people_json['height'],
            'homeworld': people_json['homeworld'],
            'mass': people_json['mass'],
            'name': people_json['name'],
            'skin_color': people_json['skin_color'],
            'species': people_json['species'],
            'starships': people_json['starships'],
            'vehicles': people_json['vehicles'],
            }    
    print(f'Загрузили json id={people_id}')

    result['films'] = await get_titles(session, people_json['films'], 'title')
    print('Получили "films" у id=', people_id)
    result['species'] = await get_titles(session, people_json['species'], 'name')
    print('Получили "species" у id=', people_id)
    result['starships'] = await get_titles(session, people_json['starships'], 'name')
    print('Получили "starships" у id=', people_id)
    result['vehicles'] = await get_titles(session, people_json['vehicles'], 'name')
    print('Получили "vehicles" у id=', people_id)

    return result


async def get_titles(session, links: list, key: str) -> str:    
    all_name = []
    for link in links:
        async with session.get(link) as response:  
            name = await response.json()
            all_name.append(name[key])
    return  ', '.join(all_name)


async def paste_to_db(results: dict):
    swapi_people = SwapiPeople(id=results['id'], birth_year=results['birth_year'])
    async with Session() as session:
        session.add(swapi_people)        
        await session.commit()
        print('Записали в БД id=', results['id'])


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all) # Cтереть все
        await conn.run_sync(Base.metadata.create_all) # Создать все
        await conn.commit()

    session = ClientSession()
    coros = (get_people(session, i) for i in range(1, 90))
    for coros_chunk in chunked(coros, CHUNK_SIZE):
        res_list = await asyncio.gather(*coros_chunk)
        res_list = [i for i in res_list if i] # Удалить пустые списки
        for res in res_list:
            asyncio.create_task(paste_to_db(res))
    await session.close()  

    tasks = set(asyncio.all_tasks()) - {asyncio.current_task()}
    for task in tasks:
        await task


start = datetime.datetime.now()
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())
print('Полное время выполнения программы:', datetime.datetime.now() - start)
