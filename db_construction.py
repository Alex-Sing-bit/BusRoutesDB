import enum

from sqlalchemy import Column, Integer, String, ForeignKey, Enum, \
    UniqueConstraint, \
    PrimaryKeyConstraint, CheckConstraint
from sqlalchemy.orm import declarative_base, relationship

DATABASE = {
    'drivername': 'postgresql+psycopg2',
    'host': 'localhost',
    'port': '5432',
    'username': 'postgres',
    'password': '1234',
    'database': 'roads',
    'query': {
    }
}

DeclarativeBase = declarative_base()


class StreetType(enum.Enum):
    avenue = 'avenue'
    street = 'street'
    lane = 'lane'
    square = 'square'


class TransportType(enum.Enum):
    bus = 'bus'
    trolleybus = 'trolleybus'
    tram = 'tram'


class BuildingType(enum.Enum):
    residential = 'residential'
    public = 'public'
    industrial = 'industrial'


class RouteType(enum.Enum):
    urban = 'urban'
    suburban = 'suburban'
    intercity = 'intercity'


long_string = 300
middle_string = 100
short_string = 50


class Street(DeclarativeBase):
    __tablename__ = 'street'

    street_id = Column(Integer, primary_key=True, autoincrement=True)
    street_name = Column(String(middle_string), nullable=False)
    street_type = Column(Enum(StreetType), nullable=False)
    district = Column(String(middle_string), nullable=False)
    __table_args__ = (
        UniqueConstraint('street_name', 'street_type'),
    )

    stops = relationship("Stop", back_populates="street", cascade="all, delete-orphan")
    buildings = relationship("Building", back_populates="street", cascade="all, delete-orphan")


class Stop(DeclarativeBase):
    __tablename__ = 'stop'

    stop_id = Column(Integer, primary_key=True, autoincrement=True)
    stop_name = Column(String(long_string), nullable=False, unique=True)
    stop_type = Column(Enum(TransportType), nullable=False)
    street_id = Column(Integer, ForeignKey('street.street_id'), nullable=False)

    street = relationship("Street", back_populates="stops")
    buildings = relationship("Building", back_populates="stop", cascade="all, delete-orphan")
    stops_to_routes = relationship("StopsToRoute", back_populates="stop", cascade="all, delete-orphan")


class Building(DeclarativeBase):
    __tablename__ = 'building'

    building_id = Column(Integer, primary_key=True, autoincrement=True)
    building_number = Column(Integer, nullable=False)
    building_type = Column(Enum(BuildingType), nullable=False)
    street_id = Column(Integer, ForeignKey('street.street_id'), nullable=False)
    stop_id = Column(Integer, ForeignKey('stop.stop_id'), nullable=False)
    __table_args__ = (
        UniqueConstraint('building_number', 'street_id'),
        CheckConstraint('building_number > 0'),
    )

    street = relationship("Street", back_populates="buildings")
    stop = relationship("Stop", back_populates="buildings")


class Route(DeclarativeBase):
    __tablename__ = 'route'

    route_id = Column(Integer, primary_key=True, autoincrement=True)
    route_number = Column(Integer, unique=True, nullable=False)
    route_type = Column(Enum(RouteType), nullable=False)
    __table_args__ = (
        CheckConstraint('route_number > 0'),
    )

    stops_to_routes = relationship("StopsToRoute", back_populates="route", cascade="all, delete-orphan")
    public_transports = relationship("PublicTransport", back_populates="route", cascade="all, delete-orphan")

class StopsToRoute(DeclarativeBase):
    __tablename__ = 'stops_to_route'

    stops_to_route_id = Column(Integer, primary_key=True, autoincrement=True)
    route_id = Column(Integer, ForeignKey('route.route_id'))
    stop_id = Column(Integer, ForeignKey('stop.stop_id'))
    stop_num_in_route = Column(Integer, nullable=False)
    __table_args__ = (
        UniqueConstraint('route_id', 'stop_id'),
        UniqueConstraint('route_id', 'stop_num_in_route'),
    )

    route = relationship("Route", back_populates="stops_to_routes")
    stop = relationship("Stop", back_populates="stops_to_routes")


class PublicTransport(DeclarativeBase):
    __tablename__ = 'public_transport'

    transport_id = Column(Integer, primary_key=True, autoincrement=True)
    transport_number = Column(String(6), unique=True, nullable=False)
    route_id = Column(Integer, ForeignKey('route.route_id'), nullable=False)
    transport_type = Column(Enum(TransportType), nullable=False)

    route = relationship("Route", back_populates="public_transports")