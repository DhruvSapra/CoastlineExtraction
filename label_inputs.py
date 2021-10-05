import rasterio as rio
from rasterio import merge
from rasterio.enums import Resampling
from rasterio.warp import calculate_default_transform, reproject

import numpy as np


def add_labels(input_path, label_path):
    with rio.open(label_path, 'r') as label_src:
        print(label_src.shape)
        print(label_src.meta)
        labels = label_src.read(1)
        with rio.open(input_path, 'r') as input_src:
            print(input_src.shape)
            print(input_src.meta)
            input_meta = input_src.meta
            input_meta.update(count = 5)

            dst_raster = np.zeros((input_src.shape[0], input_src.shape[1]))
            reprojected_labels = reproject(labels, 
                                           dst_raster, 
                                           src_transform=label_src.transform, 
                                           dst_transform=input_src.transform, 
                                           src_crs=label_src.crs, 
                                           dst_crs=input_src.crs,
                                           resampling=Resampling.bilinear)
            print(reprojected_labels[0].shape)
            with rio.open('merged_img.tif', 'w', **input_meta) as dst:
                dst.write_band(1, input_src.read(1))
                dst.write_band(2, input_src.read(2))
                dst.write_band(3, input_src.read(3))
                dst.write_band(4, input_src.read(4))
                dst.write_band(5, reprojected_labels[0].astype(rio.uint16))

# example usage
# add_labels("C:\\Users\\kjcar\\Desktop\\268898_0369619_2016-10-15_0e14_BGRN_SR_clip.tif", "C:\\Users\\kjcar\\Desktop\\2016_08.tif")

# adapted from https://mmann1123.github.io/pyGIS/docs/e_raster_reproject.html
def reproject_image(reference_image, target_image):
    with rio.open(reference_image) as dst, \
        rio.open(target_image) as src:
        print("Source CRS:", src.crs)
        print("Destination CRS:", dst.crs)

        src_transform = src.transform

        dst_transform, width, height = calculate_default_transform(
            src.crs,
            dst.crs,
            src.width,
            src.height,
            *src.bounds
        )

        dst_meta = src.meta.copy()
        dst_meta.update(
            {
                "crs": dst.crs,
                "transform": dst_transform,
                "width": width,
                "height": height,
                "nodata": 0
            }
        )

        with rio.open("data/2016_08_reprojected.tif", 'w', **dst_meta) as output:
            reproject(
                source=rio.band(src, 1),
                destination=rio.band(output, 1),
                src_transform=src.transform,
                src_crs = src.crs,
                dst_transform = dst_transform,
                dst_crs=dst.crs,
                resampling=Resampling.bilinear
            )
    
    
reference_image = "data/268898_0369619_2016-10-15_0e14_BGRN_SR_clip.tif"
target_image = "data/2016_08.tif"
reproject_image(reference_image, target_image)