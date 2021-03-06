from enum import Enum
from dataclasses import dataclass
from typing import Tuple, List, Optional, Set
import os
from datetime import datetime


class HazardType(Enum):
    VOLCANO     = 1
    EARTHQUAKE  = 2

    @classmethod
    def from_string(cls, string: str) -> "HazardType":
        """
        Example: HazardType.from_string("volcanoes")

        :param string: Either "volcanoes" or "earthquakes"
        :raises ValueError when `string not in ("volcanoes", "earthquakes")
        """
        upper_string = string.upper()
        if upper_string in HazardType.__members__:
            return HazardType[upper_string]
        else:
            raise ValueError("{} is not a valid hazard type".format(string))

    def to_string(self) -> str:
        """
        Converts a hazard type into a lowercase string.
        Examples: HazardType.to_string(HazardType.VOLCANOES) returns 'volcanoes'
                  HazardType.to_string(HazardType.EARTHQUAKES) returns 'earthquakes'
        """
        return self.name.lower()


class ImageType(Enum):
    GEO_BACKSCATTER     = 1
    GEO_COHERENCE       = 2
    GEO_INTERFEROGRAM   = 3
    ORTHO_BACKSCATTER   = 4
    ORTHO_COHERENCE     = 5
    ORTHO_INTERFEROGRAM = 6

    @classmethod
    def from_string(cls, string: str) -> "ImageType":
        upper_string = string.upper()
        if upper_string in ImageType.__members__:
            return ImageType[upper_string]
        else:
            raise ValueError("{} is not a valid image type".format(string))

    def to_string(self) -> str:
        return self.name.lower()


class SatelliteEnum(Enum):
    ERS = 1
    ENV = 2
    S1A = 3
    RS1 = 4
    RS2 = 5
    CSK = 6
    TSX = 7
    JERS = 8
    ALOS = 9
    ALOS2 = 10
    NISAR = 11

    @classmethod
    def from_string(cls, string: str) -> "SatelliteEnum":
        upper_string = string.upper()
        if upper_string in SatelliteEnum.__members__:
            return SatelliteEnum[upper_string]
        else:
            raise ValueError("{} is not a valid image type".format(string))

    def to_string(self) -> str:
        return self.name.upper()


class LatLong:
    def __init__(self, lat: float, long: float):
        self.lat: float = lat
        self.long: float = long


class Date:
    """
    Class for dates of the format YYYYMMDD

    Example:
        >>> today = Date("20190411")
        >>> print(today.date)
        20190411
        >>> print("The year is {0} in the {1}th month".format(today.date[:4], today.date[4:6]))
        The year is 2019 in the 04th month
    """

    def __init__(self, date: str):

        if self.is_valid_date(date):
            self.date = date
        else:
            raise ValueError("The date {0} is not a valid date of the form \"YYYYMMDD\"".format(date))

    @classmethod
    def is_valid_date(self, possible_date: str):
        """
        Checks if date is of format "YYYYMMDD"
        """
        if len(possible_date) == 8:
            if possible_date.isdigit():
                if 1 <= int(possible_date[4:6]) <= 12:
                    if 1 <= int(possible_date[6:]) <= 31:
                        return True
        return False

    def to_integer(self):
        return int(self.date)

    @classmethod
    def get_today(cls):
        return Date(datetime.now().strftime("%Y%m%d"))


class DateRange:
    """
    This class is used for filtering images by a range of dates.
    If `end = None`, then the date range ends on the current date
    """
    def __init__(self, start: Date, end: Optional[Date] = None):
        self.start: Date = start
        self.end: Optional[Date] = end

    def __str__(self):
        end_str = self.end.date if self.end else str(None)
        return "[{start}, {end}]".format(start=self.start.date, end=end_str)

    def date_in_range(self, date: Date):
        end_date = self.end if self.end != None else Date.get_today()
        return int(self.start) <= int(date.date) <= int(end_date)


class ImageURL():
    """
    Creates and validates a URL
    """
    def __init__(self, url: str):
        if self.is_valid_url(url):
            self.url: str = url
        else:
            raise ValueError("The url {0} is not a valid URL".format(url))

    # TODO: Add further validation
    @classmethod
    def is_valid_url(self, url):
        valid_extensions = [".jpg", ".png", ".tif", ".gif"]
        filename, file_extension = os.path.splitext(url)
        if file_extension not in valid_extensions:
            return False
        return True


class Location:
    def __init__(self, center: LatLong):

        valid_lats = self.validate_latitude(center)
        valid_lons = self.validate_longitude(center)
        if valid_lats and valid_lons:
            self.center = center
        else:
            raise Exception()

    @classmethod
    def validate_latitude(cls, lat: LatLong):
        return -90 <= float(lat.lat) <= 90

    @classmethod
    def validate_longitude(cls, lon: LatLong):
        return -180 <= float(lon.long) <= 180


@dataclass
class Satellite:
    satellite_id: SatelliteEnum
    ascending: bool

    def to_string(self):
        """
        :return: Of the form "SATID_ASC" or "SATID_DESC"
        """
        sat_id_str = self.satellite_id.to_string()

        if self.ascending:
            return sat_id_str + "_ASC"
        else:
            return sat_id_str + "_DESC"

    @classmethod
    def from_string(cls, raw_satellite: str) -> Tuple["Satellite", ...]:
        """
        The `raw_satellite` parameter can be of the following formats:

        1. "SATID" OR "SATID_BOTH" -> Tuple of both ascending and descending satellites of SATID
        2."SATID_ASC" -> Tuple of just ascending satellite SATID
        3. "SATID_DESC" -> Tuple of just descending satellite SATID
        :raises: ValueError, AscendingParseException
        :return:
        """
        if "_" in raw_satellite:
            sat_id, asc_or_desc = raw_satellite.split("_")
            asc_or_desc = asc_or_desc.lower()
            if asc_or_desc not in ('asc', 'desc', 'both'):
                raise AscendingParseException
        else:
            sat_id = raw_satellite
            asc_or_desc = 'both'

        sat_enum = SatelliteEnum.from_string(sat_id)
        asc_satellite = Satellite(satellite_id=sat_enum, ascending=True)
        desc_satellite = Satellite(satellite_id=sat_enum, ascending=False)

        if asc_or_desc == 'both':
            return asc_satellite, desc_satellite
        elif asc_or_desc == 'asc':
            return (asc_satellite,) # The way to create a 1-tuple in Python
        elif asc_or_desc == 'desc':
            return (desc_satellite,)

    def __hash__(self):
        return hash(self.to_string())


    @classmethod
    def get_satellite_name(cls) -> str:
        pass


class AscendingParseException(Exception):
    pass


@dataclass
class Hazard:
    hazard_id: str
    name: str
    hazard_type: HazardType
    location: Location
    last_updated: Date


@dataclass
class Image:
    image_id: str
    hazard_id: str
    satellite: Satellite
    image_type: ImageType
    image_date: Date
    raw_image_url: ImageURL
    tif_image_url: ImageURL
    modified_image_url: ImageURL


class HazardInfoFilter:
    """
    self.satellites: Optional[List[Satellite]]
    self.image_types: Optional[List[ImageType]]
    self.date_range: Optional[DateRange]
    self.max_num_images: int
    """

    def __init__(self,
                 satellites: Optional[List[Satellite]],
                 image_types: Optional[List[ImageType]],
                 date_range: Optional[DateRange],
                 max_num_images: int,
                 last_n_days: Optional[int]):

        self.satellites: Optional[List[Satellite]] = satellites
        self.image_types: Optional[List[ImageType]] = image_types
        self.max_num_images: int = max_num_images

        # Combine date_range and last_n_days date range into a single date range
        # We use last_n_days as the start date if it exists
        if last_n_days:
            last_n_days_date = Date(str(int(Date.get_today().date) - last_n_days))
            if date_range is None:
                new_date_range = DateRange(start=last_n_days_date)
            else:
                new_date_range = DateRange(start=last_n_days_date, end=date_range.end)
        else:
            new_date_range = date_range
        self.date_range: Optional[DateRange] = new_date_range
