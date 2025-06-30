from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import cast

import h5py
import numpy as np
import numpy.typing as npt
import pandas as pd

from nsidc.iceflow.data.models import GLAH06DataFrame

# Note: the ITRF is given by the NSIDC landing page:
# https://nsidc.org/data/glah06/versions/34#anchor-data-access-tools
# The ITRF does not appear to be present in the source data or the user guide.
GLAH06_ITRF = "ITRF2008"
VERSION = "034"
# All scalar variables with single dimension 'DS_UTCTime_40'
VARIABLES = [
    ("DS_UTCTime_40", "/Data_40HZ/DS_UTCTime_40"),
    ("i_rec_ndx", "/Data_40HZ/Time/i_rec_ndx"),
    ("i_shot_count", "/Data_40HZ/Time/i_shot_count"),
    ("d_lat", "/Data_40HZ/Geolocation/d_lat"),
    ("d_lon", "/Data_40HZ/Geolocation/d_lon"),
    ("d_elev", "/Data_40HZ/Elevation_Surfaces/d_elev"),
    ("d_refRng", "/Data_40HZ/Elevation_Surfaces/d_refRng"),
    ("d_dTrop", "/Data_40HZ/Elevation_Corrections/d_dTrop"),
    ("d_satElevCorr", "/Data_40HZ/Elevation_Corrections/d_satElevCorr"),
    ("d_GmC", "/Data_40HZ/Elevation_Corrections/d_GmC"),
    ("d_wTrop", "/Data_40HZ/Elevation_Corrections/d_wTrop"),
    ("d_beamCoelv", "/Data_40HZ/Elevation_Angles/d_beamCoelv"),
    ("d_beamAzimuth", "/Data_40HZ/Elevation_Angles/d_beamAzimuth"),
    ("d_SigBegOff", "/Data_40HZ/Elevation_Offsets/d_SigBegOff"),
    ("d_TrshRngOff", "/Data_40HZ/Elevation_Offsets/d_TrshRngOff"),
    ("d_SigEndOff", "/Data_40HZ/Elevation_Offsets/d_SigEndOff"),
    ("d_cntRngOff", "/Data_40HZ/Elevation_Offsets/d_cntRngOff"),
    ("d_isRngOff", "/Data_40HZ/Elevation_Offsets/d_isRngOff"),
    ("d_siRngOff", "/Data_40HZ/Elevation_Offsets/d_siRngOff"),
    ("d_ldRngOff", "/Data_40HZ/Elevation_Offsets/d_ldRngOff"),
    ("d_ocRngOff", "/Data_40HZ/Elevation_Offsets/d_ocRngOff"),
    ("rng_uqf_sigbeg1_flg", "/Data_40HZ/Quality/rng_uqf_sigbeg1_flg"),
    ("rng_uqf_sigend1_flg", "/Data_40HZ/Quality/rng_uqf_sigend1_flg"),
    ("rng_uqf_thres1_flg", "/Data_40HZ/Quality/rng_uqf_thres1_flg"),
    ("rng_uqf_cent1_flg", "/Data_40HZ/Quality/rng_uqf_cent1_flg"),
    ("rng_uqf_sigbeg2_flg", "/Data_40HZ/Quality/rng_uqf_sigbeg2_flg"),
    ("rng_uqf_sigend2_flg", "/Data_40HZ/Quality/rng_uqf_sigend2_flg"),
    ("rng_uqf_thres2_flg", "/Data_40HZ/Quality/rng_uqf_thres2_flg"),
    ("rng_uqf_cent2_flg", "/Data_40HZ/Quality/rng_uqf_cent2_flg"),
    ("rng_uqf_is_flg", "/Data_40HZ/Quality/rng_uqf_is_flg"),
    ("rng_uqf_si_flg", "/Data_40HZ/Quality/rng_uqf_si_flg"),
    ("rng_uqf_ld_flg", "/Data_40HZ/Quality/rng_uqf_ld_flg"),
    ("rng_uqf_oc_flg", "/Data_40HZ/Quality/rng_uqf_oc_flg"),
    ("sat_corr_flg", "/Data_40HZ/Quality/sat_corr_flg"),
    ("elev_use_flg", "/Data_40HZ/Quality/elev_use_flg"),
    ("att_pad_use_flg", "/Data_40HZ/Quality/att_pad_use_flg"),
    ("att_calc_pad_flg", "/Data_40HZ/Quality/att_calc_pad_flg"),
    ("att_lpa_flg", "/Data_40HZ/Quality/att_lpa_flg"),
    ("sigma_att_flg", "/Data_40HZ/Quality/sigma_att_flg"),
    ("i_satNdx", "/Data_40HZ/Quality/i_satNdx"),
    ("d_pctSAT", "/Data_40HZ/Quality/d_pctSAT"),
    ("elv_cnt_1_flg", "/Data_40HZ/Elevation_Flags/elv_cnt_1_flg"),
    ("elv_cnt_2_flg", "/Data_40HZ/Elevation_Flags/elv_cnt_2_flg"),
    ("elv_peak_1_flg", "/Data_40HZ/Elevation_Flags/elv_peak_1_flg"),
    ("elv_peak_2_flg", "/Data_40HZ/Elevation_Flags/elv_peak_2_flg"),
    ("elv_thres_flg", "/Data_40HZ/Elevation_Flags/elv_thres_flg"),
    ("elv_gauss_flg", "/Data_40HZ/Elevation_Flags/elv_gauss_flg"),
    ("elv_other_flg", "/Data_40HZ/Elevation_Flags/elv_other_flg"),
    ("elv_cloud_flg", "/Data_40HZ/Elevation_Flags/elv_cloud_flg"),
    ("d_TxNrg", "/Data_40HZ/Transmit_Energy/d_TxNrg"),
    ("d_d2refTrk", "/Data_40HZ/Geophysical/d_d2refTrk"),
    ("d_DEM_elv", "/Data_40HZ/Geophysical/d_DEM_elv"),
    ("d_ocElv", "/Data_40HZ/Geophysical/d_ocElv"),
    ("d_poTide", "/Data_40HZ/Geophysical/d_poTide"),
    ("d_gdHt", "/Data_40HZ/Geophysical/d_gdHt"),
    ("d_erElv", "/Data_40HZ/Geophysical/d_erElv"),
    ("d_eqElv", "/Data_40HZ/Geophysical/d_eqElv"),
    ("d_ldElv", "/Data_40HZ/Geophysical/d_ldElv"),
    ("d_deltaEllip", "/Data_40HZ/Geophysical/d_deltaEllip"),
    ("d_ElevBiasCorr", "/Data_40HZ/Geophysical/d_ElevBiasCorr"),
    ("i_DEM_hires_src_1", "/Data_40HZ/Geophysical/i_DEM_hires_src_1"),
    ("d_reflctUC", "/Data_40HZ/Reflectivity/d_reflctUC"),
    ("d_sDevNsOb1", "/Data_40HZ/Reflectivity/d_sDevNsOb1"),
    ("d_satNrgCorr", "/Data_40HZ/Reflectivity/d_satNrgCorr"),
    ("d_RecNrgAll", "/Data_40HZ/Reflectivity/d_RecNrgAll"),
    ("d_skew2", "/Data_40HZ/Waveform/d_skew2"),
    ("d_kurt2", "/Data_40HZ/Waveform/d_kurt2"),
    ("d_maxRecAmp", "/Data_40HZ/Waveform/d_maxRecAmp"),
    ("d_maxSmAmp", "/Data_40HZ/Waveform/d_maxSmAmp"),
    ("i_nPeaks1", "/Data_40HZ/Waveform/i_nPeaks1"),
    ("i_numPk", "/Data_40HZ/Waveform/i_numPk"),
    ("i_gval_rcv", "/Data_40HZ/Waveform/i_gval_rcv"),
    ("d_FRir_cldtop", "/Data_40HZ/Atmosphere/d_FRir_cldtop"),
    ("FRir_qa_flg", "/Data_40HZ/Atmosphere/FRir_qa_flg"),
    ("d_FRir_intsig", "/Data_40HZ/Atmosphere/d_FRir_intsig"),
]

TIMESTAMP_COLUMN = "utc_datetime"

DATA_COLUMNS = [
    ("i_rec_ndx", b"%d"),
    ("i_shot_count", b"%d"),
    ("d_lat", b"%f"),
    ("d_lon", b"%f"),
    ("d_elev", b"%f"),
    ("d_refRng", b"%f"),
    ("d_dTrop", b"%f"),
    ("d_satElevCorr", b"%f"),
    ("d_GmC", b"%f"),
    ("d_wTrop", b"%f"),
    ("d_beamCoelv", b"%f"),
    ("d_beamAzimuth", b"%f"),
    ("d_SigBegOff", b"%f"),
    ("d_TrshRngOff", b"%f"),
    ("d_SigEndOff", b"%f"),
    ("d_cntRngOff", b"%f"),
    ("d_isRngOff", b"%f"),
    ("d_siRngOff", b"%f"),
    ("d_ldRngOff", b"%f"),
    ("d_ocRngOff", b"%f"),
    ("rng_uqf_sigbeg1_flg", b"%d"),
    ("rng_uqf_sigend1_flg", b"%d"),
    ("rng_uqf_thres1_flg", b"%d"),
    ("rng_uqf_cent1_flg", b"%d"),
    ("rng_uqf_sigbeg2_flg", b"%d"),
    ("rng_uqf_sigend2_flg", b"%d"),
    ("rng_uqf_thres2_flg", b"%d"),
    ("rng_uqf_cent2_flg", b"%d"),
    ("rng_uqf_is_flg", b"%d"),
    ("rng_uqf_si_flg", b"%d"),
    ("rng_uqf_ld_flg", b"%d"),
    ("rng_uqf_oc_flg", b"%d"),
    ("sat_corr_flg", b"%d"),
    ("elev_use_flg", b"%d"),
    ("att_pad_use_flg", b"%d"),
    ("att_calc_pad_flg", b"%d"),
    ("att_lpa_flg", b"%d"),
    ("sigma_att_flg", b"%d"),
    ("i_satNdx", b"%d"),
    ("d_pctSAT", b"%f"),
    ("elv_cnt_1_flg", b"%d"),
    ("elv_cnt_2_flg", b"%d"),
    ("elv_peak_1_flg", b"%d"),
    ("elv_peak_2_flg", b"%d"),
    ("elv_thres_flg", b"%d"),
    ("elv_gauss_flg", b"%d"),
    ("elv_other_flg", b"%d"),
    ("elv_cloud_flg", b"%d"),
    ("d_TxNrg", b"%f"),
    ("d_d2refTrk", b"%f"),
    ("d_DEM_elv", b"%f"),
    ("d_ocElv", b"%f"),
    ("d_poTide", b"%f"),
    ("d_gdHt", b"%f"),
    ("d_erElv", b"%f"),
    ("d_eqElv", b"%f"),
    ("d_ldElv", b"%f"),
    ("d_deltaEllip", b"%f"),
    ("d_ElevBiasCorr", b"%f"),
    ("i_DEM_hires_src_1", b"%d"),
    ("d_reflctUC", b"%f"),
    ("d_sDevNsOb1", b"%f"),
    ("d_satNrgCorr", b"%f"),
    ("d_RecNrgAll", b"%f"),
    ("d_skew2", b"%f"),
    ("d_kurt2", b"%f"),
    ("d_maxRecAmp", b"%f"),
    ("d_maxSmAmp", b"%f"),
    ("i_nPeaks1", b"%d"),
    ("i_numPk", b"%d"),
    ("i_gval_rcv", b"%d"),
    ("d_FRir_cldtop", b"%f"),
    ("FRir_qa_flg", b"%d"),
    ("d_FRir_intsig", b"%f"),
]


def _utc_datetime(seconds):
    """Return 'utc_datetime' Series with values calculated from the shot data.

    The transmit time of each shot in the 1 second frame is measured as UTC seconds elapsed
    since Jan 1 2000 12:00:00 UTC. This time has been derived from the GPS time accounting
    for leap seconds.
    """
    epoc = dt.datetime(2000, 1, 1, 12, 0, 0)
    utc = seconds.apply(lambda s: epoc + dt.timedelta(seconds=s))

    return utc


def _mask_invalid(var) -> npt.NDArray[np.bool_]:
    assert len(var.shape) == 1, "Expected only 1 dimensional data"
    values = var[:]

    invalid: npt.NDArray[np.bool_] = np.full(var.shape, False)

    # Mask no data values
    if "_FillValue" in var.attrs:
        invalid |= values == var.attrs["_FillValue"][0]

    # Mask out-of-range values
    if "valid_min" in var.attrs and "valid_max" in var.attrs:
        valid_min = var.attrs["valid_min"][0]
        valid_max = var.attrs["valid_max"][0]
        invalid |= (values < valid_min) | (values > valid_max)

    return invalid


def _glah06_dataframe(filepath):
    """Returns a GLAH06 DataFrame read from an HDF5 file."""
    df = pd.DataFrame()
    with h5py.File(filepath, "r") as glah06:
        invalid_geo = None
        for name, path in VARIABLES:
            var = glah06[path]
            df[name] = var[:]

            # Mask row completely if geolocation is missing
            if name in ("d_lat", "d_lon", "d_elev"):
                if invalid_geo is None:
                    invalid_geo = np.full(var.shape, False)

                invalid_geo |= _mask_invalid(var)

    invalid_geo = cast(npt.NDArray[np.bool_], invalid_geo)
    df = df[~invalid_geo]

    return df


def _glah06_data(filepath):
    df = _glah06_dataframe(filepath)

    df["utc_datetime"] = _utc_datetime(df["DS_UTCTime_40"]) if not df.empty else None

    df = df.drop(columns="DS_UTCTime_40")

    return df


def glah06_data(filepath: Path) -> GLAH06DataFrame:
    """Return an GLAH06 file DataFrame, performing all necessary
    conversions / augmentation on the data.
    """
    df = _glah06_data(filepath)

    # Add the ITRF
    df["ITRF"] = GLAH06_ITRF
    # To be consistent with the other `nsidc-iceflow` datasets, copy the primary
    # lat/lon/elev fields to the standard "latitude", "longitude", "elevation"
    # field names.
    df["latitude"] = df["d_lat"]
    df["longitude"] = df["d_lon"]
    df["elevation"] = df["d_elev"]
    df["dataset"] = "GLAH06v034"

    # We index the data by utc datetime.
    df = df.set_index("utc_datetime")

    return GLAH06DataFrame(df)
