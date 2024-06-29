function coords = get_barycenter(varargin)
    % Calculates the barycenter position of specified stars with masses
    
    % Default values
    timeAltitude = [];
    star_info = struct('masses', {}, 'stars', {});

    % Parse input arguments
    if ~isempty(varargin)
        for k = 1:2:length(varargin)
            if strcmp(varargin{k}, 'timeAltitude')
                timeAltitude = varargin{k+1};
            elseif strcmp(varargin{k}, 'star_info')
                star_info = varargin{k+1};
            end
        end
    end
    
    % Check inputs
    if isempty(timeAltitude) || isempty(star_info)
        error('Please specify timeAltitude and star_info');
    end
    
    % Convert star masses from cell array to numeric array
    star_masses = cell2mat(star_info.masses);
    
    % Extract distance, altitude, and azimuth from timeAltitude
    distance_vector_km = timeAltitude(:, 4, :); % Distance in km
    altitude = timeAltitude(:, 2, :); % Altitude
    azimuth = timeAltitude(:, 3, :); % Azimuth
    
    % Convert distance from km to meters
    distance_vector_m = distance_vector_km * 1e3;
    
    % Calculate Cartesian coordinates
    x = distance_vector_m .* (cosd(altitude) .* cosd(azimuth));
    y = distance_vector_m .* (cosd(altitude) .* sind(azimuth));
    z = distance_vector_m .* (sind(altitude));
    
    % Calculate barycenter coordinates
    total_mass = sum(star_masses);
    cartesian_barycenter_mass = zeros(size(timeAltitude,1),3);
    for star_i = 1:numel(star_masses) 
        if strcmp("Barycenter", star_info.stars{star_i})
            continue
        end
        % if strcmp("Sun", star_info.stars{star_i})
        %     continue
        % end              
        % if strcmp("Jupiter", star_info.stars{star_i})
        %     continue
        % end        
        
        cartesian_barycenter_mass = cartesian_barycenter_mass + ...
            [   star_masses(star_i) * x(:,1, star_i), ...
                star_masses(star_i) * y(:,1, star_i), ...
                star_masses(star_i) * z(:,1, star_i)];
    end
    
    cartesian_barycenter = cartesian_barycenter_mass / total_mass;
    
    % Calculate distance_barycenter using norm
    distance_barycenter = vecnorm(cartesian_barycenter, 2, 2);
    
    % Convert barycenter coordinates back to altitude and azimuth
    altitude_barycenter = asind(cartesian_barycenter(:,3) ./ distance_barycenter);
    azimuth_barycenter = atan2d(cartesian_barycenter(:,2), cartesian_barycenter(:,1));
    
    % Store barycenter coordinates in coords array
    coords = [altitude_barycenter, azimuth_barycenter, distance_barycenter];
end
