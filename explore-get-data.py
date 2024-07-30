from typing import Literal

import earthaccess


ShortName = Literal["ILATM1B"]


def search_and_download(
    *,
    short_name: ShortName,
    bounding_box,
    temporal: tuple[str, str],
) -> list[str]:
    earthaccess.login()

    results = earthaccess.search_data(
        short_name=short_name,
        bounding_box=bounding_box,
        temporal=temporal,
    )

    downloaded_files = earthaccess.download(results, f"./data/{short_name}")

    return downloaded_files


if __name__ == "__main__":
    search_and_download(
        short_name="ILATM1B",
        bounding_box=(-103.125559, -75.180563, -102.677327, -74.798063),
        temporal=("1993-01-01", "2020-01-01"),
    )

    # results in:
    # ./data/ILATM1B/ILATM1B_20091109_203148.atm4cT3.qi
    # ./data/ILATM1B/ILATM1B_20111104_181304.ATM4BT4.qi
    # ./data/ILATM1B/ILATM1B_20121012_154650.ATM4BT4.qi
    # ./data/ILATM1B/ILATM1B_20121012_155318.ATM4BT4.qi
    # ./data/ILATM1B/ILATM1B_20121104_173026.ATM4BT4.qi
    # ./data/ILATM1B/ILATM1B_20121104_174950.ATM4BT4.qi
    # ./data/ILATM1B/ILATM1B_20141103_155257.ATM5BT4.h5
    # ./data/ILATM1B/ILATM1B_20161103_170445.ATM6AT6.h5
