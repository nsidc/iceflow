from __future__ import annotations

import datetime as dt
import time

import pandas as pd
from pyproj import Transformer


def _datetime_to_decimal_year(date):
    """Stolen from
    https://stackoverflow.com/questions/6451655/python-how-to-convert-datetime-dates-to-decimal-years
    """

    def sinceEpoch(date):
        # returns seconds since epoch
        return time.mktime(date.timetuple())

    s = sinceEpoch

    year = date.year
    startOfThisYear = dt.datetime(year=year, month=1, day=1)
    startOfNextYear = dt.datetime(year=year + 1, month=1, day=1)

    yearElapsed = s(date) - s(startOfThisYear)
    yearDuration = s(startOfNextYear) - s(startOfThisYear)
    fraction = yearElapsed / yearDuration

    return date.year + fraction


def transform_itrf(
    # TODO: function assumes pandas dataframe representing data w/ expected
    # fields.
    data: pd.DataFrame,
    target_itrf: str,
    # These two must both be specified to apply the plate model
    # step. Nothing happens if only one is given. TODO: raise an error if
    # only one is given. Can we determine the plate from the data instead of
    # requiring the user to pass?
    plate: str | None = None,
    target_epoch: str | None = None,
) -> pd.DataFrame:
    """Pipeline string for proj to transform from the source to the target
    ITRF frame and, optionally, epoch.

    TODO:
        * Update typing for function
        * Consider passing in lat/lon/elev/time directly instead of as a pandas df?
        * If this takes a pd.df w/ expected fields, one of those fields could be
          ITRF & plate, which would be used by this func.
    """
    transformed_chunks = []
    for source_itrf, chunk in data.groupby(by="ITRF"):
        # If the source ITRF is the same as the target for this chunk, skip transformation.
        if source_itrf == target_itrf:
            transformed_chunks.append(chunk)
            continue

        plate_model_step = ""
        if plate and target_epoch:
            plate_model_step = (
                f"+step +inv +init={target_itrf}:{plate} +t_epoch={target_epoch} "
            )

        pipeline = (
            f"+proj=pipeline +ellps=WGS84 "
            f"+step +proj=unitconvert +xy_in=deg +xy_out=rad "
            f"+step +proj=latlon "
            f"+step +proj=cart "
            f"+step +inv +init={target_itrf}:{source_itrf} "
            f"{plate_model_step}"
            f"+step +inv +proj=cart "
            f"+step +proj=unitconvert +xy_in=rad +xy_out=deg"
        )

        transformer = Transformer.from_pipeline(pipeline)

        decimalyears = (
            chunk.reset_index().utc_datetime.apply(_datetime_to_decimal_year).to_numpy()
        )
        # TODO: Should we create a new decimalyears when doing an epoch
        # propagation since PROJ doesn't do this?

        lats, lons, elevs, _ = transformer.transform(
            chunk.longitude,
            chunk.latitude,
            chunk.elevation,
            decimalyears,
        )

        transformed_chunk = chunk.copy()
        transformed_chunk["latitude"] = lats
        transformed_chunk["longitude"] = lons
        transformed_chunk["elevation"] = elevs
        transformed_chunks.append(transformed_chunk)

    transformed_df = pd.concat(transformed_chunks)
    transformed_df = transformed_df.reset_index().set_index("utc_datetime")

    return transformed_df