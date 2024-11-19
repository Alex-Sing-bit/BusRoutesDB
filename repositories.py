from typing import Generic, TypeVar, Optional, List, Dict, Any

from sqlalchemy import select
from sqlalchemy.orm import Session

import exceptions
from db_construction import Street, Stop, Building, Route, StopsToRoute, PublicTransport, RouteType, TransportType, \
    BuildingType, StreetType

# Общий тип для всех моделей
T = TypeVar('T')


class IRepository(Generic[T]):
    def __init__(self, session: Session, model: T):
        self.session = session
        self.model = model

    def add(self, entity: T) -> None:
        try:
            self.session.add(entity)
            self.session.commit()
        except Exception as e:
            exceptions.db_changing_exception(e)

    def add_list(self, arg: Dict[str, Any]) -> None:
        try:
            self.fix_string_args(arg)
            entity = self.model(**arg)
            self.add(entity)
        except Exception as e:
            exceptions.db_changing_exception(e)

    def get(self, entity_id: int) -> Optional[T]:
        try:
            return self.session.get(self.model, entity_id)
        except Exception as e:
            exceptions.db_changing_exception(e)
            return []

    def delete(self, entity: T) -> None:
        try:
            self.session.delete(entity)
            self.session.commit()
        except Exception as e:
            exceptions.db_changing_exception(e)

    def delete_by_id(self, id_arg: int) -> None:
        entity = self.get(id_arg)
        print(type(entity), entity)
        self.delete(entity)

    def update(self, entity: T) -> None:
        try:
            self.session.merge(entity)
            self.session.commit()
        except Exception as e:
            exceptions.db_changing_exception(e)

    def update_list(self, arg: Dict[str, Any]) -> None:
        try:
            self.fix_string_args(arg)
            entity = self.model(**arg)
            self.update(entity)
        except Exception as e:
            exceptions.db_changing_exception(e)

    def all(self) -> list[T]:
        try:
            records = self.session.query(self.model).all()
            field_values_list = []

            # Проходим по всем записям
            for record in records:
                # Извлекаем значения полей в виде словаря
                field_values = [getattr(record, column.name) for column in self.model.__table__.columns]
                field_values_list.append(field_values)

            return field_values_list
        except Exception as e:
            exceptions.db_changing_exception(e)
            return []

    def fields_list(self, instance_id):
        instance = self.session.query(self.model).get(instance_id)
        if instance is not None:
            return [getattr(instance, field.key) for field in self.model.__table__.c]
        return None

    def fix_string_args(self, arg: Dict[str, Any]):
        pass


class StreetRepository(IRepository[Street]):
    def __init__(self, session: Session):
        super().__init__(session, Street)

    def fix_string_args(self, arg: Dict[str, Any]):
        arg["street_type"] = StreetType[(arg["street_type"]).split(".")[-1]]


class StopRepository(IRepository[Stop]):
    def __init__(self, session: Session):
        super().__init__(session, Stop)

    def fix_string_args(self, arg: Dict[str, Any]):
        arg["stop_type"] = TransportType[(arg["stop_type"]).split(".")[-1]]
        arg["street_id"] = int(arg["street_id"])


class BuildingRepository(IRepository[Building]):
    def __init__(self, session: Session):
        super().__init__(session, Building)

    def fix_string_args(self, arg: Dict[str, Any]):
        arg["building_number"] = int(arg["building_number"])
        arg["building_type"] = BuildingType[(arg["building_type"]).split(".")[-1]]
        arg["stop_id"] = int(arg["stop_id"])
        arg["street_id"] = int(arg["street_id"])


class RouteRepository(IRepository[Route]):
    def __init__(self, session: Session):
        super().__init__(session, Route)

    def fix_string_args(self, arg: Dict[str, Any]):
        arg["route_number"] = int(arg["route_number"])
        arg["route_type"] = RouteType[(arg["route_type"]).split(".")[-1]]


class StopsToRouteRepository(IRepository[StopsToRoute]):
    def __init__(self, session: Session):
        super().__init__(session, StopsToRoute)

    def fix_string_args(self, arg: Dict[str, Any]):
        arg["route_id"] = int(arg["route_id"])
        arg["stop_id"] = int(arg["stop_id"])
        arg["stop_num_in_route"] = int(arg["stop_num_in_route"])


class PublicTransportRepository(IRepository[PublicTransport]):
    def __init__(self, session: Session):
        super().__init__(session, PublicTransport)

    def fix_string_args(self, arg: Dict[str, Any]):
        arg["route_id"] = int(arg["route_id"])
        arg["transport_type"] = TransportType[(arg["transport_type"]).split(".")[-1]]
