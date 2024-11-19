import random

from sqlalchemy import select

from db_construction import StreetType, TransportType, BuildingType, RouteType, Street, Stop, Building, Route, \
    StopsToRoute, PublicTransport
from exceptions import db_changing_exception, exception_message

stops_number = 20
transports_number = 12
routs_number = 15


def generate_db(session):
    try:
        _generate_streets_from_file(session)
        _generate_stops_from_file(session)
        _generate_buildings_on_streets_from_file(session)
        _generate_routes(session)
        _generate_stops_to_routes(session)
        _generate_transport(session)
    except Exception as e:
        exception_message("Ошибка генерации базы данных", e)


street_file = 'streets.txt'


def _generate_streets_from_file(session):
    d = ['Central', 'Soviet', 'North', 'South']
    k = 0
    with open(street_file, mode='r', encoding='utf-8') as st:
        s = st.readlines()
        for street in s[0].split(" "):
            add_street(session, street, StreetType.street, random.choice(d))

        for street in s[1].split(" "):
            add_street(session, street, StreetType.avenue, d[k])

        for street in s[2].split(" "):
            add_street(session, street, StreetType.lane, d[k])

        for street in s[3].split(" "):
            add_street(session, street, StreetType.square, d[k])


def _generate_stops_from_file(session):
    with open('stops.txt', mode='r', encoding='utf-8') as sp:
        s_p = sp.readlines()
        with open(street_file, mode='r', encoding='utf-8') as st:
            s = st.readlines()

            s = [strt.split(" ") for strt in s]
            s = [name.strip() for sublist in s for name in sublist]

            for name in s_p:
                add_stop(session, name, random.choice(list(TransportType)),
                         random.choice([k for k in range(1, len(s) + 1)]))


def _generate_buildings_on_streets_from_file(session):
    with open(street_file, mode='r', encoding='utf-8') as st:
        s = st.readlines()
        k = 1
        for _ in s[0].split(" "):
            _generate_buildings(session, 60, k)
            k += 1

        for _ in s[1].split(" "):
            _generate_buildings(session, 90, k)
            k += 1

        for _ in s[2].split(" "):
            _generate_buildings(session, 25, k)
            k += 1

        for _ in s[3].split(" "):
            _generate_buildings(session, 15, k)
            k += 1


def _generate_buildings(session, buildings_num: int, street_id: int):
    for i in range(1, buildings_num + 1):
        add_building(session, i, random.choice(list(BuildingType)),
                     street_id, random.choice(list(i for i in range(1, stops_number + 1))))


def _generate_routes(session):
    numbers = [i for i in range(1, routs_number + 1)]
    for _ in range(1, routs_number + 1):
        num = random.choice(numbers)
        add_route(session, num, random.choice(list(RouteType)))
        numbers.remove(num)


def _generate_stops_to_routes(session):

    for i in range(1, routs_number + 1):
        k = random.choice([i for i in range(4, routs_number)])
        stops = [i for i in range(1, stops_number + 1)]
        for j in range(1, k + 1):
            stop = random.choice(stops)
            add_stops_to_route(session, i, stop, j)
            stops.remove(stop)


def _generate_transport(session):
    route_numbers = [i for i in range(1, routs_number + 1)]
    numbers = [i for i in range(1, 10)]
    characters = [chr(i) for i in range(ord('А'), ord('Я') + 1)]
    for _ in range(0, transports_number):
        route = random.choice(route_numbers)
        number = "{}{}{}{}{}{}".format(random.choice(characters),
                                       random.choice(numbers), random.choice(numbers), random.choice(numbers),
                                       random.choice(characters), random.choice(characters))
        add_public_transport(session, number, route, random.choice(list(TransportType)))
        route_numbers.remove(route)


def add_street(session, street_name: str, street_type: StreetType, district: str):
    if street_name.strip() == "":
        db_changing_exception(Exception(""))
        return
    try:
        new_post = Street(street_name=street_name.strip(), street_type=street_type, district=district)
        session.add(new_post)
        session.commit()
    except Exception as e:
        db_changing_exception(e)
        session.rollback()


def add_stop(session, stop_name: str, stop_type: TransportType, street_id: int):
    if stop_name.strip() == "":
        print('Ошибка: stop_name - пустая строка')
        return
    try:
        new_stop = Stop(stop_name=stop_name.strip(), stop_type=stop_type, street_id=street_id)
        session.add(new_stop)
        session.commit()
    except Exception as e:
        db_changing_exception(e)
        session.rollback()


def add_building(session, building_number: int, building_type: BuildingType, street_id: int, stop_id: int):
    try:
        new_building = Building(building_number=building_number, building_type=building_type,
                                street_id=street_id, stop_id=stop_id)
        session.add(new_building)
        session.commit()
    except Exception as e:
        db_changing_exception(e)
        session.rollback()


def add_route(session, route_number: int, route_type: RouteType):
    try:
        new_route = Route(route_number=route_number, route_type=route_type)
        session.add(new_route)
        session.commit()
    except Exception as e:
        db_changing_exception(e)
        session.rollback()


def add_stops_to_route(session, route_id: int, stop_id: int, stop_num_in_route: int):
    try:
        new_stops_to_route = StopsToRoute(route_id=route_id, stop_id=stop_id,
                                          stop_num_in_route=stop_num_in_route)
        session.add(new_stops_to_route)
        session.commit()
    except Exception as e:
        db_changing_exception(e)
        session.rollback()


def add_public_transport(session, transport_number: str, route_id: int, transport_type: TransportType):
    try:
        new_public_transport = PublicTransport(transport_number=transport_number,
                                               route_id=route_id, transport_type=transport_type)
        session.add(new_public_transport)
        session.commit()
    except Exception as e:
        db_changing_exception(e)
        session.rollback()
