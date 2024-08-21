from __future__ import annotations

import datetime as dt
from pathlib import Path

import cartopy.crs as ccrs
import matplotlib.pyplot as plt

from nsidc.iceflow.api import fetch_iceflow_df
from nsidc.iceflow.data.models import (
    ATM1BDataset,
    DatasetSearchParameters,
)
from nsidc.iceflow.itrf.converter import transform_itrf


def viz_with_cartopy(results):
    """Visualize the example results.

    Stock background imagery isn't high res enough to be useful. Maybe can find
    some high-res satellite imagery for this area?
    """

    # visualize results.
    ax = plt.axes(projection=ccrs.SouthPolarStereo(central_longitude=0))
    ax.coastlines(resolution="50m", color="black", linewidth=1)
    # ax.set_extent(matplotlib_extent, ccrs.PlateCarree())
    plt.scatter(
        results.longitude.values,
        results.latitude.values,
        c=results.elevation.values,
        cmap="viridis",
        transform=ccrs.PlateCarree(),
    )
    ax.stock_img()
    plt.colorbar(label="elevation", shrink=0.5, extend="both")
    plt.show()


def viz_with_mpl_3d(df, transformed_df, sampled_epoch):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(
        df.longitude.values,
        df.latitude.values,
        df.elevation.values,
        color="blue",
        marker="o",
    )

    ax.scatter(
        transformed_df.longitude.values,
        transformed_df.latitude.values,
        transformed_df.elevation.values,
        color="green",
        marker="x",
    )

    ax.scatter(
        sampled_epoch.longitude.values,
        sampled_epoch.latitude.values,
        sampled_epoch.elevation.values,
        color="red",
        marker="v",
    )

    ax.set_xlabel("longitude (degrees)", labelpad=10)
    ax.set_ylabel("latitude (degrees)", labelpad=10)
    ax.set_zlabel("elevation (m)", labelpad=10)

    plt.show()


if __name__ == "__main__":
    data_path = Path("./downloaded-data/")
    atm1b_v1_dataset = ATM1BDataset(version="1")

    # This finds and downloads a single source file,
    # `ILATM1B_20091109_203148.atm4cT3.qi`, and reads the data into a pandas
    # dataframe. These data are in ITRF2005.
    iceflow_df = fetch_iceflow_df(
        dataset_search_params=DatasetSearchParameters(
            dataset=atm1b_v1_dataset,
            bounding_box=(-103.125559, -75.180563, -102.677327, -74.798063),
            temporal=(dt.date(2009, 11, 1), dt.date(2009, 12, 31)),
        ),
        output_dir=data_path,
        output_itrf=None,
    )

    # Transform to ITRF 2014
    itrf2014 = transform_itrf(
        data=iceflow_df,
        target_itrf="ITRF2014",
    )

    # Here we can see the maximum difference between between points before and
    # after the transformation from ITRF2005 to ITRF2014 is small:
    # (itrf2014[["longitude", "latitude", "elevation"]] - iceflow_df[["longitude", "latitude", "elevation"]]).abs().max()
    # longitude    7.992290e-08
    # latitude     1.850908e-08
    # elevation    7.642244e-03
    # The largest elevation difference is 0.007 meters - 7 mm!

    # Now lets assume we need to propagate the data to a target epoch of
    # 2019.7, which corresponds to September 13, 2019. This accounts for
    # continental plate motion.
    itrf2014_epoch_2019_7 = transform_itrf(
        data=iceflow_df,
        target_itrf="ITRF2014",
        target_epoch="2019.7",
    )

    # Here we can see the maximum difference between between points before and
    # after the transformation from ITRF2005 to ITRF2014 with a target epoch of
    # 2019.7 is still small:
    # (itrf2014_epoch_2019_7[["longitude", "latitude", "elevation"]] - iceflow_df[["longitude", "latitude", "elevation"]]).abs().max()
    # longitude    5.552263e-06
    # latitude     4.895740e-07
    # elevation    7.729957e-03
    # The largest elevation difference is 0.008 meters - 8 mm!

    # Because there is a lot of data, we reduce for demonstration purposes
    # filter_condition = ((iceflow_df.reset_index().index > 50) & (iceflow_df.reset_index().index < 140))
    # this is actually pretty good.
    filter_condition = (iceflow_df.reset_index().index > 50) & (
        iceflow_df.reset_index().index < 60
    )
    sampled_iceflow_df = iceflow_df[filter_condition]
    sampled_itrf2014 = itrf2014[filter_condition]
    sampled_itrf2014_epoch_2019_7 = itrf2014_epoch_2019_7[filter_condition]

    # now visualize the untransformed points, the ITRF-2014 transformed points,
    # and the ITRF-2014 epoch-propagated points
    viz_with_mpl_3d(sampled_iceflow_df, sampled_itrf2014, sampled_itrf2014_epoch_2019_7)
