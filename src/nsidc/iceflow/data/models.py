from __future__ import annotations

import datetime as dt
from typing import Literal

import pandera as pa
import pydantic
from earthaccess.results import DataGranule
from pandera.typing import DataFrame, Index, Series

from nsidc.iceflow.itrf import ITRF_REGEX


class CommonDataColumnsSchema(pa.DataFrameModel):
    utc_datetime: Index[pa.dtypes.DateTime] = pa.Field(check_name=True)
    ITRF: Series[str] = pa.Field(str_matches=ITRF_REGEX.pattern)
    latitude: Series[float] = pa.Field(coerce=True)
    longitude: Series[float] = pa.Field(coerce=True)
    elevation: Series[float] = pa.Field(coerce=True)


class ATM1BSchema(CommonDataColumnsSchema):
    # Data fields unique to ATM1B data.
    rel_time: Series[float] = pa.Field(nullable=True, coerce=True)
    xmt_sigstr: Series[float] = pa.Field(nullable=True, coerce=True)
    rcv_sigstr: Series[float] = pa.Field(nullable=True, coerce=True)
    azimuth: Series[float] = pa.Field(nullable=True, coerce=True)
    pitch: Series[float] = pa.Field(nullable=True, coerce=True)
    roll: Series[float] = pa.Field(nullable=True, coerce=True)
    gps_pdop: Series[float] = pa.Field(nullable=True, coerce=True)
    gps_time: Series[float] = pa.Field(nullable=True, coerce=True)
    passive_signal: Series[float] = pa.Field(nullable=True, coerce=True)
    passive_footprint_latitude: Series[float] = pa.Field(nullable=True, coerce=True)
    passive_footprint_longitude: Series[float] = pa.Field(nullable=True, coerce=True)
    passive_footprint_synthesized_elevation: Series[float] = pa.Field(
        nullable=True, coerce=True
    )
    pulse_width: Series[float] = pa.Field(nullable=True, coerce=True)


# Note/TODO: the ILVIS2 data contain multiple sets of lat/lon/elev. The common
# schema assumes one set of lat/lon/elev which is used for the ITRF
# transformation code.
class ILVIS2Schema(CommonDataColumnsSchema):
    # Common columns
    LFID: Series[float] = pa.Field(nullable=True, coerce=True)
    SHOTNUMBER: Series[float] = pa.Field(nullable=True, coerce=True)
    TIME: Series[float] = pa.Field(nullable=True, coerce=True)
    ZG: Series[float] = pa.Field(nullable=True, coerce=True)
    GLAT: Series[float] = pa.Field(nullable=True, coerce=True)
    GLON: Series[float] = pa.Field(nullable=True, coerce=True)
    HLAT: Series[float] = pa.Field(nullable=True, coerce=True)
    HLON: Series[float] = pa.Field(nullable=True, coerce=True)
    ZH: Series[float] = pa.Field(nullable=True, coerce=True)

    # V104-specific
    CLAT: Series[float] = pa.Field(nullable=True, coerce=True)
    CLON: Series[float] = pa.Field(nullable=True, coerce=True)
    ZC: Series[float] = pa.Field(nullable=True, coerce=True)

    # V202B-specific
    AZIMUTH: Series[float] = pa.Field(nullable=True, coerce=True)
    CHANNEL_RH: Series[float] = pa.Field(nullable=True, coerce=True)
    CHANNEL_ZG: Series[float] = pa.Field(nullable=True, coerce=True)
    CHANNEL_ZT: Series[float] = pa.Field(nullable=True, coerce=True)
    COMPLEXITY: Series[float] = pa.Field(nullable=True, coerce=True)
    INCIDENT_ANGLE: Series[float] = pa.Field(nullable=True, coerce=True)
    RANGE: Series[float] = pa.Field(nullable=True, coerce=True)
    RH10: Series[float] = pa.Field(nullable=True, coerce=True)
    RH15: Series[float] = pa.Field(nullable=True, coerce=True)
    RH20: Series[float] = pa.Field(nullable=True, coerce=True)
    RH25: Series[float] = pa.Field(nullable=True, coerce=True)
    RH30: Series[float] = pa.Field(nullable=True, coerce=True)
    RH35: Series[float] = pa.Field(nullable=True, coerce=True)
    RH40: Series[float] = pa.Field(nullable=True, coerce=True)
    RH45: Series[float] = pa.Field(nullable=True, coerce=True)
    RH50: Series[float] = pa.Field(nullable=True, coerce=True)
    RH55: Series[float] = pa.Field(nullable=True, coerce=True)
    RH60: Series[float] = pa.Field(nullable=True, coerce=True)
    RH65: Series[float] = pa.Field(nullable=True, coerce=True)
    RH70: Series[float] = pa.Field(nullable=True, coerce=True)
    RH75: Series[float] = pa.Field(nullable=True, coerce=True)
    RH80: Series[float] = pa.Field(nullable=True, coerce=True)
    RH85: Series[float] = pa.Field(nullable=True, coerce=True)
    RH90: Series[float] = pa.Field(nullable=True, coerce=True)
    RH95: Series[float] = pa.Field(nullable=True, coerce=True)
    RH96: Series[float] = pa.Field(nullable=True, coerce=True)
    RH97: Series[float] = pa.Field(nullable=True, coerce=True)
    RH98: Series[float] = pa.Field(nullable=True, coerce=True)
    RH99: Series[float] = pa.Field(nullable=True, coerce=True)
    RH100: Series[float] = pa.Field(nullable=True, coerce=True)
    TLAT: Series[float] = pa.Field(nullable=True, coerce=True)
    TLON: Series[float] = pa.Field(nullable=True, coerce=True)
    ZT: Series[float] = pa.Field(nullable=True, coerce=True)

    class Config:
        # This ensures all columns are present, regardless of the date. Granules
        # before 2017 use the V104 fields and anything after uses the v202b
        # fields. The data type for all values must be `float` because the null
        # value is `np.nan` - a float.
        add_missing_columns = True


class GLAH06Schema(CommonDataColumnsSchema):
    # Note: all of these variables are extracted from the "Data_40HZ"
    # group. There is also a "Data_1HZ" group, which contains similar variables,
    # but does not include the elevation data and appears to be a downsampled
    # version of the "Data_40HZ" group. See
    # https://github.com/nsidc/iceflow/issues/43.
    i_rec_ndx: Series[int] = pa.Field(coerce=True)
    i_shot_count: Series[int] = pa.Field(coerce=True)
    d_lat: Series[float]
    d_lon: Series[float]
    d_elev: Series[float]
    d_refRng: Series[float]
    d_dTrop: Series[float]
    d_satElevCorr: Series[float]
    d_GmC: Series[float]
    d_wTrop: Series[float]
    d_beamCoelv: Series[float]
    d_beamAzimuth: Series[float]
    d_SigBegOff: Series[float]
    d_TrshRngOff: Series[float]
    d_SigEndOff: Series[float]
    d_cntRngOff: Series[float]
    d_isRngOff: Series[float]
    d_siRngOff: Series[float]
    d_ldRngOff: Series[float]
    d_ocRngOff: Series[float]
    rng_uqf_sigbeg1_flg: Series[int] = pa.Field(coerce=True)
    rng_uqf_sigend1_flg: Series[int] = pa.Field(coerce=True)
    rng_uqf_thres1_flg: Series[int] = pa.Field(coerce=True)
    rng_uqf_cent1_flg: Series[int] = pa.Field(coerce=True)
    rng_uqf_sigbeg2_flg: Series[int] = pa.Field(coerce=True)
    rng_uqf_sigend2_flg: Series[int] = pa.Field(coerce=True)
    rng_uqf_thres2_flg: Series[int] = pa.Field(coerce=True)
    rng_uqf_cent2_flg: Series[int] = pa.Field(coerce=True)
    rng_uqf_is_flg: Series[int] = pa.Field(coerce=True)
    rng_uqf_si_flg: Series[int] = pa.Field(coerce=True)
    rng_uqf_ld_flg: Series[int] = pa.Field(coerce=True)
    rng_uqf_oc_flg: Series[int] = pa.Field(coerce=True)
    sat_corr_flg: Series[int] = pa.Field(coerce=True)
    elev_use_flg: Series[int] = pa.Field(coerce=True)
    att_pad_use_flg: Series[int] = pa.Field(coerce=True)
    att_calc_pad_flg: Series[int] = pa.Field(coerce=True)
    att_lpa_flg: Series[int] = pa.Field(coerce=True)
    sigma_att_flg: Series[int] = pa.Field(coerce=True)
    i_satNdx: Series[int] = pa.Field(coerce=True)
    d_pctSAT: Series[float]
    elv_cnt_1_flg: Series[int] = pa.Field(coerce=True)
    elv_cnt_2_flg: Series[int] = pa.Field(coerce=True)
    elv_peak_1_flg: Series[int] = pa.Field(coerce=True)
    elv_peak_2_flg: Series[int] = pa.Field(coerce=True)
    elv_thres_flg: Series[int] = pa.Field(coerce=True)
    elv_gauss_flg: Series[int] = pa.Field(coerce=True)
    elv_other_flg: Series[int] = pa.Field(coerce=True)
    elv_cloud_flg: Series[int] = pa.Field(coerce=True)
    d_TxNrg: Series[float]
    d_d2refTrk: Series[float]
    d_DEM_elv: Series[float]
    d_ocElv: Series[float]
    d_poTide: Series[float]
    d_gdHt: Series[float]
    d_erElv: Series[float]
    d_eqElv: Series[float]
    d_ldElv: Series[float]
    d_deltaEllip: Series[float]
    d_ElevBiasCorr: Series[float]
    i_DEM_hires_src_1: Series[int] = pa.Field(coerce=True)
    d_reflctUC: Series[float]
    d_sDevNsOb1: Series[float]
    d_satNrgCorr: Series[float]
    d_RecNrgAll: Series[float]
    d_skew2: Series[float]
    d_kurt2: Series[float]
    d_maxRecAmp: Series[float]
    d_maxSmAmp: Series[float]
    i_nPeaks1: Series[int] = pa.Field(coerce=True)
    i_numPk: Series[int] = pa.Field(coerce=True)
    i_gval_rcv: Series[int] = pa.Field(coerce=True)
    d_FRir_cldtop: Series[float]
    FRir_qa_flg: Series[int] = pa.Field(coerce=True)
    d_FRir_intsig: Series[float]


IceflowDataFrame = DataFrame[CommonDataColumnsSchema]
ATM1BDataFrame = DataFrame[ATM1BSchema]
ILVIS2DataFrame = DataFrame[ILVIS2Schema]
GLAH06DataFrame = DataFrame[GLAH06Schema]

ATM1BShortName = Literal["ILATM1B", "BLATM1B"]
DatasetShortName = ATM1BShortName | Literal["ILVIS2"] | Literal["GLAH06"]


class Dataset(pydantic.BaseModel):
    short_name: DatasetShortName
    version: str

    @property
    def subdir_name(self):
        return f"{self.short_name}_{self.version}"


class ATM1BDataset(Dataset):
    short_name: ATM1BShortName


class ILATM1BDataset(ATM1BDataset):
    short_name: ATM1BShortName = "ILATM1B"
    version: Literal["1", "2"]


class BLATM1BDataset(ATM1BDataset):
    short_name: ATM1BShortName = "BLATM1B"
    # There is only 1 version of BLATM1B
    version: Literal["1"] = "1"


class ILVIS2Dataset(Dataset):
    short_name: DatasetShortName = "ILVIS2"
    version: Literal["1", "2"]


class GLAH06Dataset(Dataset):
    short_name: DatasetShortName = "GLAH06"
    # Note: some dataset versions are padded with zeros like GLAH06. NSIDC
    # documentation refers to "version 34", but CMR only recognizes "034".  As a
    # rule-of-thumb, ICESat-2, SMAP, and GLAH/GLA datasets have zero padding.
    version: Literal["034"] = "034"


class BoundingBox(pydantic.BaseModel):
    lower_left_lon: float
    lower_left_lat: float
    upper_right_lon: float
    upper_right_lat: float

    def __init__(self, *args, **kwargs):
        """Accept either named args, one arg for each coord, or an iterable of
        `(lower_left_lon, lower_left_lat, upper_right_lon, upper_right_lat)`."""
        if args:
            if len(args) == 1 and isinstance(args[0], list | tuple):
                # The first arg should be treated like a tuple of
                # (lower_left_lon, lower_left_lat, upper_right_lon,
                # upper_right_lat)
                args = tuple(args[0])
            # Each arg should be treated as one of (lower_left_lon,
            # lower_left_lat, upper_right_lon, upper_right_lat).
            if len(args) != 4:
                raise ValueError(
                    "Expected four values for bounding box:"
                    " (lower_left_lon, lower_left_lat, upper_right_lon, upper_right_lat)"
                )
            # Set kwargs if args are given.
            kwargs = {
                "lower_left_lon": args[0],
                "lower_left_lat": args[1],
                "upper_right_lon": args[2],
                "upper_right_lat": args[3],
            }

        # Initialize the model.
        super().__init__(**kwargs)

    def __iter__(self):
        """Return bounding box as a iter (list/tuple)."""
        return iter(
            (
                self.lower_left_lon,
                self.lower_left_lat,
                self.upper_right_lon,
                self.upper_right_lat,
            )
        )

    def __getitem__(self, idx):
        if isinstance(idx, int):
            return list(self.__iter__())[idx]
        elif isinstance(idx, str):
            return getattr(self, idx)
        else:
            raise TypeError(
                "Getitem on BoundingBox must be int (e.g. 0)"
                " or str (e.g., 'lower_left_lon')."
            )


ALL_DATASETS: list[Dataset] = [
    ILATM1BDataset(version="1"),
    ILATM1BDataset(version="2"),
    BLATM1BDataset(version="1"),
    ILVIS2Dataset(version="1"),
    ILVIS2Dataset(version="2"),
    GLAH06Dataset(),
]


class DatasetSearchParameters(pydantic.BaseModel):
    datasets: list[Dataset] = ALL_DATASETS
    bounding_box: BoundingBox
    temporal: tuple[dt.datetime | dt.date, dt.datetime | dt.date]


class IceflowSearchResult(pydantic.BaseModel):
    dataset: Dataset
    granules: list[DataGranule]

    # Pydantic can't infer what `DataGranule` is. This ignores validation for
    # this that type
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)


IceflowSearchResults = list[IceflowSearchResult]
