from flask import Flask, render_template, request
from flask_csp.csp import csp_default, csp_header
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker

from db_construction import DATABASE, DeclarativeBase, Street, Stop, Building, Route, PublicTransport, StopsToRoute
from db_interactions import generate_db
from exceptions import exception_message, web_exception
from repositories import (StreetRepository, StopRepository, RouteRepository,
                          StopsToRouteRepository, BuildingRepository, PublicTransportRepository, IRepository)

app = Flask(__name__)
default_policies = csp_default()
default_policies.update({
    'default-src': "'self'",
    'script-src': "'self' 'unsafe-inline' https://code.jquery.com https://cdn.datatables.net",
    'style-src': "'self' 'unsafe-inline' https://cdn.datatables.net",
    'img-src': "'self'",
    'child-src': "'self'",
    'report-uri': '/csp_report'
})


class DBConnector:
    def __init__(self):
        self.session = None

    def db_connection(self):
        try:
            engine = create_engine(URL(**DATABASE), echo=True)

            session = sessionmaker(bind=engine)

            self.session = session()
            DeclarativeBase.metadata.create_all(engine)
        except Exception as e:
            exception_message("Ошибка подключения к бд", e)

    def db_generation(self):
        try:
            generate_db(self.session)
        except Exception as e:
            exception_message("Ошибка генерации базы данных", e)

    def db_disconnect(self):
        self.session.close()

    def repository_creation(self):
        return (StreetRepository(self.session), StopRepository(self.session),
                BuildingRepository(self.session), RouteRepository(self.session),
                PublicTransportRepository(self.session), StopsToRouteRepository(self.session))


db_connector = DBConnector()
db_connector.db_connection()
db_connector.db_generation()
(street_repository, stop_repository, building_repository,
 route_repository, public_transport_repository, stops_to_route_repository) = db_connector.repository_creation()


@app.route('/show_tables', methods=['GET', 'POST'])
@csp_header()
def show_tables():
    selected_table = request.form.get('table_selection', 'Улица')
    table_data = choose_repository(selected_table).all()
    column_names = find_columns_name(selected_table)
    print("Street", selected_table)

    return render_template('show_tables.html', table_data=table_data, selected_table=selected_table,
                           column_count=len(column_names), column_names=column_names)


@app.route('/change_info', methods=['GET', 'POST'])
@csp_header()
def change_info():
    selected_table = request.form.get('table_selection', 'Улица')
    column_names = find_columns_name(selected_table)

    if request.method == 'POST':
        s = post_for_change_info()
        if s is not None:
            return s
    return render_template('change_info.html', selected_table=selected_table, object=column_names,
                           input_fields=[])


def post_for_change_info():
    action = request.form.get('action')
    selected_table = request.form.get("selected_table")
    column_names = find_columns_name(selected_table)
    if action == 'get_by_id':
        _id = request.form.get(request.form.get('id_name'))
        try:
            int_id = int(_id)
            s = entity_in_strings(selected_table, int_id)
            if not s:
                web_exception(Exception("Такого id нет в базе данных"))
                return render_template('change_info.html', selected_table=selected_table,
                                       object=column_names, input_fields=[])
            return render_template('change_info.html', selected_table=selected_table,
                                   object=column_names, input_fields=s)
        except ValueError:
            web_exception(Exception("Некорректное значение id"))
    elif action in ['update', 'add', 'delete']:
        data = handle_update_add_delete(action)
        return render_template('change_info.html', selected_table=selected_table,
                               object=column_names, input_fields=data)


def handle_update_add_delete(action):
    selected_table = request.form.get('selected_table')
    data = {key: request.form[key] for key in request.form}
    data.pop('action')
    data.pop('selected_table')
    data.pop('id_name')

    r = choose_repository(selected_table)
    if action == 'update':
        r.update_list(data)
    elif action == 'add':
        data.pop(request.form.get('id_name'))
        r.add_list(data)
    elif action == 'delete':
        id_name = data.get(request.form.get('id_name'))
        r.delete_by_id(int(id_name))
    return data


def entity_in_strings(selected_table: str, id: int) -> list[str]:
    r = choose_repository(selected_table)
    s = r.fields_list(id)

    return s


def choose_repository(selected_table: str) -> IRepository:
    if selected_table == "Улица":
        return street_repository
    elif selected_table == "Остановка":
        return stop_repository
    elif selected_table == "Здание":
        return building_repository
    elif selected_table == "Маршрут":
        return route_repository
    elif selected_table == "Общественный транспорт":
        return public_transport_repository
    elif selected_table == "Остановки на маршруте":
        return stops_to_route_repository


def find_columns_name(selected_table: str) -> list[str]:
    column_names = []

    if selected_table == "Улица":
        column_names = list(Street.__table__.columns)
    elif selected_table == "Остановка":
        column_names = list(Stop.__table__.columns)
    elif selected_table == "Здание":
        column_names = list(Building.__table__.columns)
    elif selected_table == "Маршрут":
        column_names = list(Route.__table__.columns)
    elif selected_table == "Общественный транспорт":
        column_names = list(PublicTransport.__table__.columns)
    elif selected_table == "Остановки на маршруте":
        column_names = list(StopsToRoute.__table__.columns)

    return [column.name for column in column_names]


@app.route('/', methods=['GET'])
@csp_header()
def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
    db_connector.db_disconnect()
