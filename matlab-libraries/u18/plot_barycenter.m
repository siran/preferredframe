% Example plot setup (adjust as needed)
figure;
hold on;
grid on;
xlabel('Azimuth (degrees)');
ylabel('Altitude (degrees)');
zlabel('Distance to Barycenter (meters)');
title('Movement of Barycenter');

% Extracting barycenter coordinates and distance
altitude_barycenter = squeeze(timeAltitude(:, 5, :)); % Barycenter altitude
azimuth_barycenter = squeeze(timeAltitude(:, 6, :));  % Barycenter azimuth
distance_barycenter = squeeze(timeAltitude(:, 7, :)); % Distance to barycenter

% Plotting the trajectory of the barycenter in 3D
plot3(azimuth_barycenter, altitude_barycenter, distance_barycenter, '-o');

% Adjust plot settings if needed
view(3); % Set view to 3D