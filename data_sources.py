from multigrids import tools, TemporalGrid
import glob
import os
import numpy as np
from spicebox import raster, transforms

from sites import LOCATIONS

data_root = '../../data'

DATA_TYPE = "multigrid"

REGION = 'ACP'



path_dict = {
   "ewp": os.path.join(data_root, 'V1/precipitation/early-winter', REGION, 'v3/cru/', DATA_TYPE),
   "fwp": os.path.join(data_root, 'V1/precipitation/full-winter', REGION, 'v3/cru/', DATA_TYPE),
   "tdd": os.path.join(data_root, 'V1/degree-day/thawing', REGION, 'v4/cru/', DATA_TYPE),
   "fdd": os.path.join(data_root, 'V1/degree-day/freezing', REGION, 'v4/cru/', DATA_TYPE),
   "cp":  os.path.join(data_root, 'V1/thermokarst/initiation-regions', REGION, 'v5-d/PDM-5var/without_predisp/', DATA_TYPE)
}

view_path = os.path.join(data_root, 'V1', 'cp-explorer-views')
try: 
    os.makedirs (view_path)
except:
    pass

import tempfile
tempfile.tempdir = os.path.join(data_root,'tmp')

predisp_model, pm_md = raster.load_raster(
    os.path.join(
        data_root, 
        'V1/thermokarst/predisposition-model/ACP/v2',
        'ACP-tk-predisp-model.tif'
    )
)


def load_dataset(dataset_name, path, sites, start_timestep):

    if DATA_TYPE == "tiff":

        files = glob.glob(os.path.join(path, "*.tif"))

        load_params = {
            "method": "tiff",
            "directory": path
        }
        create_params = {
            'start_timestep': start_timestep,
            'raster_metadata': tools.get_raster_metadata(files[0])
        }

        full_data = tools.load_and_create(load_params, create_params)
    else:
        files = glob.glob(os.path.join(path, "*.yml"))
        full_data = TemporalGrid(files[0])
    
    # data_by_site = {}
    for site in sites:
        
        if site == "ACP":
            start_year = full_data.config['start_timestep']

            grid_shape = full_data.config['grid_shape']
            full_data.config['mean'] = np.nanmean(full_data.grids[:1951-start_year],axis=0).reshape(grid_shape)
            sites[site]['data'][dataset_name] = full_data
            pdm = predisp_model
            print 


        else:
            current_vp = os.path.join(view_path, '%s-%s.yml' % (site, dataset_name))
            try:
                view = TemporalGrid(current_vp)
                print('view loaded:', current_vp )
            except FileNotFoundError as e: 
                print (e)
                view = full_data.zoom_to(
                    sites[site]['geolocation'], location_format="WGS84"
                )
                start_year = view.config['start_timestep']
                grid_shape = view.config['grid_shape']
                # print(view.grids[:1951-start_year].mean(axis=0))
                view.config['mean'] = np.nanmean(view.grids[:1951-start_year],axis=0).reshape(grid_shape)
                # print(view.config['mean'])

                
                view.save(current_vp)

            

            sites[site]['data'][dataset_name] = view
            geo = transforms.from_wgs84(
                sites[site]['geolocation'], pm_md['projection']
            )
            pixel = transforms.to_pixel(geo, full_data.config['raster_metadata']['transform']).astype(int)
            pdm = raster.zoom_to(predisp_model, pixel) 

        pdm[pdm<0] = -np.inf
        pdm = pdm / 100

        sites[site]['predisp_model'] = pdm[::-1]
    return sites


def load_all(path_dict, sites, start_timestep=1901):

    sites = LOCATIONS
    for dataset in ["fdd", "tdd", "ewp", "fwp", "cp"]:
        sites = load_dataset(
            dataset , path_dict[dataset], sites, start_timestep
        )

    return sites

GLOBAL_SITE_DATA = load_all(path_dict, LOCATIONS, 1901)

def create_data(site_data, init_year = 1902):

    # # print('a')
    # to_x_geo = lambda x, y, gt: gt[0] + (x + .5)*gt[1] + (y + .5)*gt[2]
    # to_y_geo = lambda x, y, gt: gt[3] + (x + .5)*gt[4] + (y + .5)*gt[5]
    # md =  multigrid.config['raster metadata']
    

    # in_crs = CRS.from_wkt(md.projection)
    # gps = CRS.from_epsg(4326)
    # transformer = Transformer.from_crs(in_crs, gps)
    # # print('b')
    # x = np.zeros(init.shape)
    # y = np.zeros(init.shape)
    # x[:] = range(init.shape[1])
    # y.T[:] = range(init.shape[0])

    # # print('c')

    # x_geo = to_x_geo(x,y,md.transform)
    # y_geo = to_y_geo(x,y,md.transform)
    # print('d')
    data = dict(
        cp=[site_data['data']['cp'][init_year][::-1]], 
        cp_vals=[site_data['data']['cp'][init_year][::-1]],
        # x_geo = [x_geo[::-1]],
        # y_geo = [y_geo[::-1]],
        # lat = [transformer.transform(x_geo,y_geo)[0] [::-1]],
        # long = [transformer.transform(x_geo,y_geo)[1] [::-1]],
        # raster_metadata = [md]
    )
    # print('e')

    data['current_year'] = [init_year]
    data['current_average'] = [0]
    data['tdd_last'] = [site_data['data']['fdd'][init_year - 1][::-1]]
    data['tdd'] = [site_data['data']['fdd'][init_year][::-1]]
    data['fdd'] = [site_data['data']['fdd'][init_year - 1][::-1]]
    data['ewp'] = [site_data['data']['ewp'][init_year - 1][::-1]]
    data['fwp'] = [site_data['data']['fwp'][init_year - 1][::-1]]
    data['predisp'] = [predisp_model]

    return data

def create_area_average_data(multigrid):

    average = []
    for yr in range(multigrid.config['num_timesteps']):
        # print(multigrid.grids[yr])
        average.append(np.nanmean(multigrid.grids[yr]))
    return average
