import laspy
import rasterio
import numpy as np

#load the laz file (must be same crs as raster!)
las = laspy.read('/mnt/disk2/qgis/marin_city/USGS_LPC_CA_NoCal_Wildfires_B5b_QL1_2018_w2280n1968_reproj_26910.las')

#load the geotiff file(must be same crs as lidar!)
ndvi = rasterio.open('/mnt/disk2/qgis/marin_city/naip_2018_marin_county/marin_city_naip_tiles/USGS_LPC_CA_NoCal_Wildfires_B5b_QL1_2018_w2280n1968_naip_NDVI.tif')
rgb = rasterio.open('/mnt/disk2/qgis/marin_city/naip_2018_marin_county/marin_city_naip_tiles/USGS_LPC_CA_NoCal_Wildfires_B5b_QL1_2018_w2280n1968_hn_naip.tif')
#get the affine transform of the raster
transform = ndvi.transform

#get the x and y coordinates of each point
coords = np.vstack((las.points['X']*las.header.scale[0] + las.header.offset[0], las.points['Y']*las.header.scale[1] + las.header.offset[1]))

#apply the affine transform to get the corresponding pixel coordinates
rows, cols = rasterio.transform.rowcol(transform, coords[0], coords[1])

#convert rows and cols to numpy arrays
rows = np.array(rows)
cols = np.array(cols)

#ensure that the rows and cols are within the bounds of the raster
valid = (0 <= rows) & (rows < ndvi.height) & (0 <= cols) & (cols < ndvi.width)
rgb_valid = (0 <= rows) & (rows < rgb.height) & (0 <= cols) & (cols < rgb.width)
print(f"Total points: {len(las.points)}")
print(f"Valid points: {np.sum(valid)}")
#initialize a new array to hold the color data
colors = np.full((len(las.points),), -0, dtype=np.float32)
red_color = np.full((len(las.points),), -0, dtype=np.float32)
green_color = np.full((len(las.points),), -0, dtype=np.float32)
blue_color = np.full((len(las.points),), -0, dtype=np.float32)
#use the row, col indices to get the NDVI values
colors[valid] = ndvi.read(1)[rows[valid], cols[valid]]
print(f"NDVI range: {np.min(colors[valid])} to {np.max(colors[valid])}")

red_color[rgb_valid] = rgb.read(1)[rows[rgb_valid], cols[rgb_valid]]
green_color[rgb_valid] = rgb.read(2)[rows[rgb_valid], cols[rgb_valid]]
blue_color[rgb_valid] = rgb.read(3)[rows[rgb_valid], cols[rgb_valid]]

#add NDVI as an extra dimension
las.add_extra_dim(laspy.ExtraBytesParams(name="ndvi", type=np.float32))

#assign NDVI values to the new dimension
las['ndvi'][:] = colors
#assign rgb values to the existing dimensions:
las['red'][:] = red_color
las['green'][:] = green_color
las['blue'][:] = blue_color
#write the output file
las.write('/mnt/disk2/qgis/marin_city/USGS_LPC_CA_NoCal_Wildfires_B5b_QL1_2018_w2280n1968_reproj_26910_colorized_w_ndvi_and_rgb.laz')
