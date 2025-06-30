from __future__ import annotations

import calendar
import datetime as dt
from typing import cast

import pandas as pd
import pandera as pa
import pyproj
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


def _check_valid_proj_step(proj_str) -> bool:
    """Check if the source/target ITRF pair can be expanded.

    Returns `True` if the combination is valid. Otherwise `False`.

    The combination is valid only if there is an init file on the proj data path
    matching the `source_itrf` that has an entry matching the `target_itrf`. See
    https://proj.org/en/9.3/resource_files.html#init-files for more info.
    """
    try:
        pyproj.Transformer.from_pipeline(proj_str)
        return True
    except pyproj.exceptions.ProjError:
        return False


def _itrf_transformation_step(source_itrf: str, target_itrf: str) -> str:
    """Get the ITRF transformation step for the given source/target ITRF.

    The transformation step returned by this function performs a helmert
    transform (see
    https://proj.org/en/9.4/operations/transformations/helmert.html).

    The parameters for the helmert transform come from proj init files (see
    https://proj.org/en/9.3/resource_files.html#init-files). For example,
    `+init=ITRF2014:ITRF2008` looks up the ITRF2008 helmert transformation step
    in the ITRF2014 data file (see
    https://github.com/OSGeo/PROJ/blob/master/data/ITRF2014).
    """
    # The `+inv` reverses the transformation. So `+init=ITRF2014:ITRF2008`
    # performs a helmert transform from ITRF2008 to ITRF2014.  This is the most
    # common case for `nsidc-iceflow`, because we tend to be targeting pre-icesat2
    # data for transformation to ITRF2014 (icesat2), so try this first.
    inv_itrf_transformation_step = f"+step +inv +init={target_itrf}:{source_itrf}"
    if _check_valid_proj_step(inv_itrf_transformation_step):
        return inv_itrf_transformation_step

    # Forward helmert transformation. `+init=ITRF2014:ITRF2008`
    # performs a helmert transform from ITRF2014 to ITRF2008.
    fwd_itrf_transformation_step = f"+step +init={source_itrf}:{target_itrf}"
    if _check_valid_proj_step(fwd_itrf_transformation_step):
        return fwd_itrf_transformation_step

    # There may not be a pre-defined helmert transformation. The user may want
    # to craft their own transformation pipeline.
    err_msg = (
        f"Failed to find a pre-defined ITRF transformation between {source_itrf} and {target_itrf}."
        " ITRF transformation parameters are provided by proj's ITRF init files."
        " Consider upgrading proj to ensure the latest data is available and try again."
        " See https://proj.org/en/latest/resource_files.html#init-files for more information."
        f" If no pre-defined transformation is available for {source_itrf} -> {target_itrf},"
        " it may be possible to define your own transformation using parameters found at https://itrf.ign.fr/."
        " See https://proj.org/en/latest/operations/transformations/helmert.html for more information."
    )
    raise RuntimeError(err_msg)


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
    """Transform the data's latitude/longitude/elevation variables from the
    source ITRF to the target ITRF.

    If a `target_epoch` is given, coordinate propagation is performed via a
    plate motion model (PMM) defined for the target_itrf. The target epoch
    determines the number of years into the future/past the observed points
    should be propagated. For example, if a point's observation date
    (`t_observed`) is 1993.0 (1993-01-01T00:00:00) and the target_epoch is
    2011.0 (2011-01-01T00:00:00), the point will be propagated forward 18
    years. Note that not all ITRFs have PMMs defined for them. The PMM used is
    defined for the target_epoch, so it is likely to be most accurate for points
    observed near the ITRF's defined epoch.

    All ITRF and PMM transformations are dependent on the user's `proj`
    installation's ITRF init files (see
    https://proj.org/en/9.3/resource_files.html#init-files). For example,
    ITRF2014 parameters are defined here:
    https://github.com/OSGeo/PROJ/blob/8b65d5b14e2a8fbb8198335019488a2b2968df5c/data/ITRF2014.

    Note that ILVIS2 data contain more than one set of
    latitude/longitude/elevation variables (e.g., HLAT/HLON/ZH,
    CLAT/CLON/ZC). This function only transforms the primary
    latitude/longitude/elevation fields in the provided dataframe. Use the
    `ilvis2_coordinate_set` kwarg on `read_iceflow_datafile(s)` to select an
    different primary set of latitude/longitude/elevation fields. Alternatively,
    manually set the fields:
    ```
    # TLAT/TLON/TZ are only available in ILVIS2v2 data:
    sel_ilvis2v2 = data.dataset == "ILVIS2v2"
    data.loc[sel_ilvis2v2, ["latitude", "longitude", "elevation"]] = data.loc[sel_ilvis2v2, ["TLAT", "TLON", "ZT"]]
    ```
    """
    if not check_itrf(target_itrf):
        err_msg = (
            f"The provided ITRF string was not recognized: {target_itrf}."
            " ITRF strings should be in the form 'ITRFYYYY'."
        )
        raise ValueError(err_msg)

    transformed_chunks = []
    for source_itrf, chunk in data.groupby(by="ITRF"):
        source_itrf = cast(str, source_itrf)
        # If the source ITRF is the same as the target for this chunk, skip transformation.
        if source_itrf == target_itrf and target_epoch is None:
            transformed_chunks.append(chunk)
            continue

        plate_model_step = ""
        if target_epoch:
            if not plate:
                plate = plate_name(Point(chunk.longitude.mean(), chunk.latitude.mean()))
            plate_model_step = (
                # Perform coordinate propagation to the target epoch using the
                # provided plate motion model (PMM).
                # This step uses the target_itrf's init file to lookup the
                # associated plate's PMM parameters. For example, ITRF2014
                # parameters are defined here:
                # https://github.com/OSGeo/PROJ/blob/8b65d5b14e2a8fbb8198335019488a2b2968df5c/data/ITRF2014.
                # The step is inverted because proj defined `t_epoch` as the
                # "central epoch" - not the "target epoch. The transformation
                # uses a delta defined by `t_observed - t_epoch` that are
                # applied to the PMM's rate of change to propagate the point
                # into the past/future. See
                # https://proj.org/en/9.5/operations/transformations/helmert.html#mathematical-description
                # for more information.
                # For example, if a point's observation date
                # (`t_observed`) is 1993.0 (1993-01-01T00:00:00) and the t_epoch
                # is 2011.0 (2011-01-01T00:00:00), then the delta is 1993 -
                # 2011: -18. We need to invert the step so that the point is
                # propagated forward in time, from 1993 to 2011.
                f"+step +inv +init={target_itrf}:{plate} +t_epoch={target_epoch}"
            )
            if not _check_valid_proj_step(plate_model_step):
                err_msg = f"Failed to find pre-defined plate-model parameters for {target_itrf}:{plate}"
                raise RuntimeError(err_msg)

        itrf_transformation_step = _itrf_transformation_step(source_itrf, target_itrf)

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
            f"{itrf_transformation_step} "
            # See above for definition.
            f"{plate_model_step} "
            # Convert back from cartesian to lat/lon coordinates
            f"+step +inv +proj=cart "
            # Convert lon/lat from radians back to degrees.
            # TODO: remove this if the initial conversion to radians above is not needed
            f"+step +proj=unitconvert +xy_in=rad +xy_out=deg"
        )

        transformer = pyproj.Transformer.from_pipeline(pipeline)

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
