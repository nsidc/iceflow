from __future__ import annotations

import calendar
import datetime as dt

import pandas as pd
import pandera as pa
from pyproj import Transformer
from shapely.geometry.point import Point

from nsidc.iceflow.data.models import IceflowDataFrame
from nsidc.iceflow.itrf import check_itrf
from nsidc.iceflow.itrf.plate_boundaries import plate_name


def _datetime_to_decimal_year(date):
    """Stolen from
    https://stackoverflow.com/questions/6451655/python-how-to-convert-datetime-dates-to-decimal-years,
    with one modification: `calendar.timegm` is used to set the epoch instead of
    `time.mktime`, which assumes local time.
    """

    def sinceEpoch(date):
        # returns seconds since epoch
        return calendar.timegm(date.timetuple())

    s = sinceEpoch

    year = date.year
    startOfThisYear = dt.datetime(year=year, month=1, day=1)
    startOfNextYear = dt.datetime(year=year + 1, month=1, day=1)

    yearElapsed = s(date) - s(startOfThisYear)
    yearDuration = s(startOfNextYear) - s(startOfThisYear)
    fraction = yearElapsed / yearDuration

    return date.year + fraction


@pa.check_types()
def transform_itrf(
    data: IceflowDataFrame,
    target_itrf: str,
    target_epoch: str | None = None,
    # If a target epoch is given, the plate name can be given. If a target_epoch
    # is given but the plate name is not, each source ITRF is grouped together
    # and the mean of that chunk is used to determine the plate name.
    plate: str | None = None,
) -> IceflowDataFrame:
    """Transform the data's lon/lat/elev from the source ITRF to the target ITRF.

    If a `target_epoch` is given, coordinate propagation is performed via a
    plate motion model.
    """
    if not check_itrf(target_itrf):
        err_msg = (
            f"The provided ITRF string was not recognized: {target_itrf}."
            " ITRF strings should be in the form 'ITRFYYYY'."
        )
        raise ValueError(err_msg)

    transformed_chunks = []
    for source_itrf, chunk in data.groupby(by="ITRF"):
        # If the source ITRF is the same as the target for this chunk, skip transformation.
        if source_itrf == target_itrf and target_epoch is None:
            transformed_chunks.append(chunk)
            continue

        plate_model_step = ""
        if target_epoch:
            if not plate:
                plate = plate_name(Point(chunk.longitude.mean(), chunk.latitude.mean()))
            plate_model_step = (
                # Perform coordinate propagation to the given epoch using the
                # provided plate motion model (PMM).  An example is given in the
                # message of this commit:
                # https://github.com/OSGeo/PROJ/commit/403f930355926aced5caba5bfbcc230ad152cf86
                f"+step +init={target_itrf}:{plate} +t_epoch={target_epoch} "
            )

        itrf_transformation_step = ""
        if source_itrf != target_itrf:
            # This performs a helmert transform (see
            # https://proj.org/en/9.4/operations/transformations/helmert.html). `+init=ITRF2014:ITRF2008`
            # looks up the ITRF2008 helmert transformation step in the ITRF2014
            # data file (see
            # https://proj.org/en/9.3/resource_files.html#init-files and e.g.,
            # https://github.com/OSGeo/PROJ/blob/master/data/ITRF2014). The
            # `+inv` reverses the transformation. So `+init=ITRF2014:ITRF2008`
            # performs a helmert transform from ITRF2008 to ITRF2014.
            itrf_transformation_step = f"+step +inv +init={target_itrf}:{source_itrf} "

        pipeline = (
            # This initializes the pipeline and declares the use of the WGS84
            # ellipsoid for all of the following steps. See
            # https://proj.org/en/9.5/operations/pipeline.html.
            f"+proj=pipeline +ellps=WGS84 "
            # Performs unit conversion from lon/lat degrees to radians.
            # TODO: This step appears to be unnecessary. Removing it does not appear to
            # affect the output. The following steps require that the
            # coordinates be geodedic, which could be radians or degrees.
            f"+step +proj=unitconvert +xy_in=deg +xy_out=rad "
            # This step explicitly sets the projection as lat/lon. It won't
            # change the coordinates, but they will be identified as geodetic,
            # which is necessary for the next steps.
            f"+step +proj=latlon "
            # Convert from lat/lon/elev geodetic coordinates to cartesian
            # coordinates, which are required for the following steps.
            # See: https://proj.org/en/9.5/operations/conversions/cart.html
            f"+step +proj=cart "
            # ITRF transformation. See above for definition.
            f"{itrf_transformation_step}"
            # See above for definition.
            f"{plate_model_step}"
            # Convert back from cartesian to lat/lon coordinates
            f"+step +inv +proj=cart "
            # Convert lon/lat from radians back to degrees.
            # TODO: remove this if the initial conversion to radians above is not needed
            f"+step +proj=unitconvert +xy_in=rad +xy_out=deg"
        )

        transformer = Transformer.from_pipeline(pipeline)

        decimalyears = (
            chunk.reset_index().utc_datetime.apply(_datetime_to_decimal_year).to_numpy()
        )
        # TODO: Should we create a new decimalyears when doing an epoch
        # propagation since PROJ doesn't do this?

        lons, lats, elevs, _ = transformer.transform(
            chunk.longitude,
            chunk.latitude,
            chunk.elevation,
            decimalyears,
        )

        transformed_chunk = chunk.copy()
        transformed_chunk["latitude"] = lats
        transformed_chunk["longitude"] = lons
        transformed_chunk["elevation"] = elevs
        transformed_chunk["ITRF"] = target_itrf
        transformed_chunks.append(transformed_chunk)

    transformed_df = pd.concat(transformed_chunks)
    transformed_df = transformed_df.reset_index().set_index("utc_datetime")
    return IceflowDataFrame(transformed_df)
