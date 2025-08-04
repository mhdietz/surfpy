-- Weather Station Migration SQL
-- Replace met_buoy_id with weather_station_ids array

UPDATE surf_spots SET weather_station_ids = ARRAY['AP803','C9585','XCDC1'] WHERE slug = 'steamer-lane';
UPDATE surf_spots SET weather_station_ids = ARRAY['C9585','AP803','CTOC1'] WHERE slug = 'privates';
UPDATE surf_spots SET weather_station_ids = ARRAY['C9585','AP803','CTOC1'] WHERE slug = 'pleasure-point';
UPDATE surf_spots SET weather_station_ids = ARRAY['KHAF'] WHERE slug = 'pacifica-north';
UPDATE surf_spots SET weather_station_ids = ARRAY['KHAF'] WHERE slug = 'pacifica-south';
UPDATE surf_spots SET weather_station_ids = ARRAY['KHAF','KOAK','LAHC1'] WHERE slug = 'montara';
UPDATE surf_spots SET weather_station_ids = ARRAY['KHAF','LAHC1'] WHERE slug = 'princeton-jetty';
UPDATE surf_spots SET weather_station_ids = ARRAY['MDEC1','D3169'] WHERE slug = 'ocean-beach-central';
UPDATE surf_spots SET weather_station_ids = ARRAY['MDEC1','D3169'] WHERE slug = 'ocean-beach-north';
UPDATE surf_spots SET weather_station_ids = ARRAY['MDEC1','D3169'] WHERE slug = 'ocean-beach-south';
UPDATE surf_spots SET weather_station_ids = ARRAY['CAPC1','KNFG','ORTSD'] WHERE slug = 'san-onofre';
UPDATE surf_spots SET weather_station_ids = ARRAY['CAPC1','ORTSD','KNFG'] WHERE slug = 'trestles';
UPDATE surf_spots SET weather_station_ids = ARRAY['KJFK','KFRG','KLGA'] WHERE slug = 'lido-beach';
UPDATE surf_spots SET weather_station_ids = ARRAY['KBLM','KWRI','KJFK'] WHERE slug = 'manasquan';
UPDATE surf_spots SET weather_station_ids = ARRAY['KJFK','KLGA','KNYC'] WHERE slug = 'rockaways';
UPDATE surf_spots SET weather_station_ids = ARRAY['KBLM','KWRI','KJFK'] WHERE slug = 'belmar';
