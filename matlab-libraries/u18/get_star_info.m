% loads star_info into current workspace
star_info.stars = {'HIP54589', 'Sun', 'Moon', 'Jupiter', 'Venus', 'Mars', 'Barycenter'};
star_info.colors = { ...
    [0.0, 0.0, 1.0],    ... % Blue for HIP54589
    [1.0, 1.0, 0.0],    ... % Yellow for Sun
    [0.0, 0.0, 0.0],    ... % Black for Moon
    [0.6, 0.3, 0.0],    ... % Brown for Jupiter
    [0.3, 0.3, 0.3],    ... % Light Gray for Venus
    [1.0, 0.0, 0.0],     ... % Red for Mars
    [0.8, 0.8, 0.8],     ... % Dark gray for Barycenter
};
star_info.linestyles = { ...
    'none',    ... % Blue for HIP54589
    'none',    ... % Yellow for Sun
    'none',    ... % Black for Moon
    'none',    ... % Brown for Jupiter
    'none',    ... % Light Gray for Venus
    'none',     ... % Red for Mars
    'none',     ... % Red for Barycenteer
}; 
star_info.markers = { ...
    '.',    ... % Blue for HIP54589
    'o',    ...    % Yellow for Sun
    '*',    ...    % Black for Moon
    '>',    ... % Brown for Jupiter
    '<',    ... % Light Gray for Venus
    'x',     ...   % Red for Mars
    '*',     ...   % Red for Barycenter
};
star_info.masses = {
    1, ...  % HIP54589
    1.98885E30, ... % Sun
    7.3477E22, ... % Moon
    1.898E27, ... % Jupiter
    4.867E24, ... % Venus
    6.39E23, ... % Mars
    1, ... % Barycenter
 };
 % masses = {1, 0, 7.3477E22, 0, 0, 0};
star_info.G = 0.000000000066743;
