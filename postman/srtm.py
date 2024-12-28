import io
import os
import zipfile

import rasterio
import rioxarray
import urllib3

TMP = "/tmp/srtm"


def _basename(i_lat: int, i_lon: int) -> str:
    return f"srtm_{i_lon:02d}_{i_lat:02d}"


def tile(latitude: float, longitude: float):
    # lat = 60 - 5 * (index - 1)
    # lon = -180 + 5 * (index - 1)
    i_lat = int((60 - latitude) / 5 + 1)
    i_lon = int((180 + longitude) / 5 + 1)
    return i_lat, i_lon


def download(i_lat, i_lon):
    url = f"https://srtm.csi.cgiar.org/wp-content/uploads/files/srtm_5x5/TIFF/{_basename(i_lat, i_lon)}.zip"
    print("downloading", url)
    response = urllib3.request("GET", url)
    assert response.status == 200
    os.makedirs(TMP, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(response.data)) as data:
        for item in data.infolist():
            with data.open(item) as memory_file:
                out_name = f"{TMP}/{item.filename}"
                # print("write", out_name)
                with open(out_name, "wb") as out_file:
                    out_file.write(memory_file.read())


def sample(latitude: float, longitude: float) -> float:
    i_lat, i_lon = tile(latitude, longitude)
    filename = f"{TMP}/{_basename(i_lat, i_lon)}.tif"
    # print("sample", filename, "at", latitude, longitude)
    if not os.path.exists(filename):
        download(i_lat, i_lon)
    dataset = rioxarray.open_rasterio(filename)
    out = dataset.interp(x=longitude, y=latitude, method="linear").item()
    return out
