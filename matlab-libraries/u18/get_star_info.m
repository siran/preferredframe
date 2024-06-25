% loads star_info into current workspace
stars = {'HIP54589', 'Sun', 'Moon', 'Jupiter', 'Venus', 'Mars'};
colors = { ...
    [0.0, 0.0, 1.0],    ... % Blue for HIP54589
    [1.0, 1.0, 0.0],    ... % Yellow for Sun
    [0.0, 0.0, 0.0],    ... % Black for Moon
    [0.6, 0.3, 0.0],    ... % Brown for Jupiter
    [0.7, 0.7, 0.7],    ... % Light Gray for Venus
    [1.0, 0.0, 0.0]     ... % Red for Mars
};
masses = {nan, 1.98885E30, 7.3477E22, 1.898E27, 4.867E24, 6.39E23};
G = 0.000000000066743;

star_info.stars = stars;
star_info.colors = colors;
star_info.masses = masses;
star_info.G = G;
