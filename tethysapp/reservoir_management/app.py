# This python script tells the app how to navigate between html pages. When you want to add a new page to the app, create an html page,
# refer to it in the url_maps function here, and add a link to the new page in the base.html

#This is also where you put the information, icon, color, etc of the app itself.

from tethys_sdk.base import TethysAppBase, url_map_maker
from tethys_sdk.app_settings import SpatialDatasetServiceSetting
from tethys_sdk.permissions import Permission, PermissionGroup


class ReservoirManagement(TethysAppBase):
    name = 'Herramientas de Operaciones de los Embalses'
    index = 'reservoir_management:home'
    icon = 'reservoir_management/images/LOGO.png'
    package = 'reservoir_management'
    root_url = 'reservoir-management'
    color = '#01AEBF'
    description = ''
    tags = ''
    enable_feedback = False
    feedback_emails = []

    def url_maps(self):
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
            UrlMap(
                name='home',
                url='reservoir-management',
                controller='reservoir_management.controllers.home'
            ),
            UrlMap(name='reportar',
                   url='reservoir-management/reportar',
                   controller='reservoir_management.controllers.reportar'
            ),
            UrlMap(name='main_handler',
                   url='reservoir-management/sites/{site_name}',
                   controller='reservoir_management.controllers.site_handler'
            ),
            UrlMap(
                name='append-res-info',
                url='reservoir-management/append-res-info',
                controller='reservoir_management.ajax_controllers.append_res_info'
            ),
            UrlMap(
                name='forecastdata',
                url='reservoir-management/forecastdata',
                controller='reservoir_management.ajax_controllers.forecastdata'
            ),
            UrlMap(
                name='recentdata',
                url='reservoir-management/getrecentdata',
                controller='reservoir_management.ajax_controllers.getrecentdata'
            ),
            UrlMap(
                name='get-forecast-curve',
                url='reservoir-management/get-forecast-curve',
                controller='reservoir_management.controllers.get_forecast_curve'
            ),
            UrlMap(
                name='check-spreadsheet',
                url='reservoir-management/check-spreadsheet',
                controller='reservoir_management.ajax_controllers.check_spreadsheet'
            ),
        )

        return url_maps


    def permissions(self):

        update_data = Permission(
            name='update_data',
            description='Update and Report input data'
        )

        admin = PermissionGroup(
            name='admin',
            permissions=(update_data,)
        )


        permissions = (admin,)

        return permissions

    #These are the setting to connect to the geoserver (where the shapefiles are stored). You will also have to connect in tethys environment
    def spatial_dataset_service_settings(self):
        sds_settings = (
            SpatialDatasetServiceSetting(
                name='main_geoserver',
                description='spatial dataset service for app to use',
                engine=SpatialDatasetServiceSetting.GEOSERVER,
                required=True,
            ),
        )

        return sds_settings
