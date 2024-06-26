global timeAltitude

% Load star information
get_star_info

% Initialize timeAltitude
timeAltitude = [];

% Loop through each star
for starname_i = 1:length(star_info.stars)
    star_name = star_info.stars{starname_i}
    if strcmp("Barycenter", star_name)
        continue
    end

    height_star_data_path = 'D:\Users\an\experimento-usb-interferometro\height-star\';
    altitude_filename = [height_star_data_path 'heightstar-' star_name '-' ...
        datestr(date_start, 'YYYY') '-' datestr(date_start, 'mm') '.csv' ];  
    
    loadfile = true;
    % todo: implement cache
    if loadfile && exist(altitude_filename, 'file')
        fprintf(['Loading altitude/azimuth for star ' star_name '\n'])

        % Read altitude/azimuth data
        rawData = readcell(altitude_filename);

        for r = 1:size(rawData, 1)
            t = r;
            timeAltitude(t, 1, starname_i) = datenum(datetime(rawData{r, 1}, ...
                'InputFormat', 'yyyy-MM-dd''T''HH:mm:ss')) + processing_session.add_hours / 24;
            timeAltitude(t, 2, starname_i) = rawData{r, 5}; % equatorial altitude
            timeAltitude(t, 3, starname_i) = rawData{r, 4}; % equatorial azimuth
            if size(rawData, 2) > 5 && ~strcmp(rawData{r, 7}, 'undefined')
                timeAltitude(t, 4, starname_i) = rawData{r, 7}; % distance to Earth in km
            else
                timeAltitude(t, 4, starname_i) = 1; % assume distance of 1 km if undefined
            end
        end
    end
end

% Calculate barycenter for all stellar objects
coords_barycenter = get_barycenter('timeAltitude', timeAltitude, 'star_info', star_info);

% Update timeAltitude with barycenter data
timeAltitude(:, 1, 7) = timeAltitude(:, 1, 1); % Barycenter altitude
timeAltitude(:, 2, 7) = coords_barycenter(:, 1); % Barycenter altitude
timeAltitude(:, 3, 7) = coords_barycenter(:, 2); % Barycenter azimuth
timeAltitude(:, 4, 7) = coords_barycenter(:, 3); % Distance to barycenter


a=1