from noaamodel import NOAAModel
from location import Location
from buoydata import BuoyData
from swell import Swell
import units
from datetime import datetime

class WaveModel(NOAAModel):

    _base_multigrid_url = 'http://nomads.ncep.noaa.gov:9090/dods/wave/mww3/{0}/{1}{0}_{2}.ascii?time[{5}:{6}],dirpwsfc.dirpwsfc[{5}:{6}][{3}][{4}],htsgwsfc.htsgwsfc[{5}:{6}][{3}][{4}],perpwsfc.perpwsfc[{5}:{6}][{3}][{4}],swdir_1.swdir_1[{5}:{6}][{3}][{4}],swdir_2.swdir_2[{5}:{6}][{3}][{4}],swell_1.swell_1[{5}:{6}][{3}][{4}],swell_2.swell_2[{5}:{6}][{3}][{4}],swper_1.swper_1[{5}:{6}][{3}][{4}],swper_2.swper_2[{5}:{6}][{3}][{4}],ugrdsfc.ugrdsfc[{5}:{6}][{3}][{4}],vgrdsfc.vgrdsfc[{5}:{6}][{3}][{4}],wdirsfc.wdirsfc[{5}:{6}][{3}][{4}],windsfc.windsfc[{5}:{6}][{3}][{4}],wvdirsfc.wvdirsfc[{5}:{6}][{3}][{4}],wvhgtsfc.wvhgtsfc[{5}:{6}][{3}][{4}],wvpersfc.wvpersfc[{5}:{6}][{3}][{4}]'

    def create_ascii_url(self, location, start_time_index, end_time_index):
        timestamp = self.latest_model_time()
        datestring = timestamp.strftime('%Y%m%d')
        hourstring = timestamp.strftime('%Hz')

        lat_index, lon_index = self.location_index(location)
        url = self._base_multigrid_url.format(datestring, self.name, hourstring, lat_index, lon_index, start_time_index, end_time_index)
        return url

    def to_buoy_data(self):
        buoy_data = []
        if not self.data:
            return buoy_data
        elif len(self.data['time']) < 1:
            return buoy_data

        for i in range(0, len(self.data['time'])):
            buoy_data_point = BuoyData(units.Units.metric)
            raw_time = (self.data['time'][i] - units.epoch_days_since_zero) * 24 * 60 * 60
            buoy_data_point.date = datetime.utcfromtimestamp(raw_time)
            buoy_data_point.wave_summary.direction = self.data['dirpwsfc'][i]
            buoy_data_point.wave_summary.compass_direction = units.degree_to_direction(buoy_data_point.wave_summary.direction)
            buoy_data_point.wave_summary.wave_height = self.data['htsgwsfc'][i]
            buoy_data_point.wave_summary.period = self.data['perpwsfc'][i]

            if self.data['swell_1'][i] < 9.0e20 and self.data['swper_1'][i] < 9.0e20 and self.data['swdir_1'][i] < 9.0e20:
                swell_1 = Swell(units.Units.metric)
                swell_1.direction = self.data['swdir_1'][i]
                swell_1.compass_direction = units.degree_to_direction(swell_1.direction)
                swell_1.wave_height = self.data['swell_1'][i]
                swell_1.period = self.data['swper_1'][i]
                buoy_data_point.swell_components.append(swell_1)

            if self.data['swell_2'][i] < 9.0e20 and self.data['swper_2'][i] < 9.0e20 and self.data['swdir_2'][i] < 9.0e20:
                swell_2 = Swell(units.Units.metric)
                swell_2.direction = self.data['swdir_2'][i]
                swell_2.compass_direction = units.degree_to_direction(swell_2.direction)
                swell_2.wave_height = self.data['swell_2'][i]
                swell_2.period = self.data['swper_2'][i]
                buoy_data_point.swell_components.append(swell_2)

            if self.data['wvhgtsfc'][i] < 9.0e20 and self.data['wvpersfc'][i] < 9.0e20 and self.data['wvdirsfc'][i] < 9.0e20:
                wind_swell = Swell(units.Units.metric)
                wind_swell.direction = self.data['wvdirsfc'][i]
                wind_swell.compass_direction = units.degree_to_direction(wind_swell.direction)
                wind_swell.wave_height = self.data['wvhgtsfc'][i]
                wind_swell.period = self.data['wvpersfc'][i]
                buoy_data_point.swell_components.append(wind_swell)

            buoy_data_point.wind_direction = self.data['wdirsfc'][i]
            buoy_data_point.wind_speed = self.data['windsfc'][i]

            buoy_data.append(buoy_data_point)

        return buoy_data


def us_east_coast_wave_model():
    return WaveModel('multi_1.at_10m', 'Multi-grid wave model: US East Coast 10 arc-min grid', Location(0.00, 260.00), Location(55.00011, 310.00011), 0.167, 0.125)

def us_west_coast_wave_model():
    return WaveModel('multi_1.wc_10m', 'Multi-grid wave model: US West Coast 10 arc-min grid', Location(25.00, 210.00), Location(50.00005, 250.00008), 0.167, 0.125)

def pacific_islands_wave_model():
    return WaveModel('multi_1.ep_10m', 'Multi-grid wave model: Pacific Islands (including Hawaii) 10 arc-min grid', Location(-20.00, 130.00), Location(30.0001, 215.00017), 0.167, 0.125)
