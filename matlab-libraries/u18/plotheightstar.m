% plot height of star
if exist('timeAltitude') && ~isempty(timeAltitude)
    holdStatus = ishold;
    hold on
    ax = gca;
    height = diff(ax.YLim);
    yyaxis right
    ax.YColor = [0 0 0];
    ylimites = [-100 100];
    ylim(ylimites)

    ax = gca;
    ax.YTick = [-90 -80:20:80 90];

    vertical_steps = -90:180/20:90;
    ylabel(['Altitude(°)'])

    % % % % % % % % % % % % % % % % % % % % % % % % % % 
    stars = {'HIP54589', 'Sun', 'Moon', "Jupiter", "Venus", "Mars"};
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
    % % % % % % % % % % % % % % % % % % % % % % % % % % % 

    plot_handles = gobjects(size(timeAltitude,3), 1); % Preallocate handles

    for starname_i = 1:numel(stars)
        starname = stars{starname_i};
        if ax.XLim == [0 360]
            x = 0:360;
            % if strcmp(starname, 'HIP54589')
                altitudes = pchip(timeAltitude(:,1, starname_i), ....
                    timeAltitude(:,2, starname_i), ...
                    xts(1):(xts(end)-xts(1))/360:xts(end));                
                y = altitudes;

                % azimuths = pchip(timeAltitude(:,1, starname_i), ....
                    % timeAltitude(:,3, starname_i), ...
                    % xts(1):(xts(end)-xts(1))/360:xts(end));                

            % elseif strcmp(starname, 'Sun') || strcmp(starname, 'Moon')
            %     distances_km= pchip(timeAltitude(:,1, starname_i), ....
            %         timeAltitude(:,4, starname_i), ...
            %         xts(1):(xts(end)-xts(1))/360:xts(end));
            % 
            %     % normalize and scale to -90:90
            %     distances_km_norm = (distances_km - distance_star_km{starname_i})/max(distances_km - distance_star_km{starname_i})*180-90;
            %     y = distances_km_norm;
            % 
            % end
        else
            % if strcmp(starname, 'HIP54589')
                altitudes = pchip(timeAltitude(:,1, starname_i), ....
                    timeAltitude(:,2, starname_i), ...
                    xts);                
                x = xts;
                y = altitudes;

                % azimuths = pchip(timeAltitude(:,1, starname_i), ....
                    % timeAltitude(:,3, starname_i), ...
                    % xts);                
                % x = xts;
                % plot(x, azimuths, [colors{starname_i} '.-'], 'lineWidth', 3);
          
            % elseif strcmp(starname, 'Sun') || strcmp(starname, 'Moon')
            %     mass_i = masses{starname_i};
            %     distances_km_all = timeAltitude(:,4, starname_i);
            %     e_density_inv_all = 1./(G*mass_i^2./(8*pi*(distances_km_all*1E3).^4));
            %     minp = min((e_density_inv_all));
            %     maxp = max((e_density_inv_all));                
            % 
            %     distances_km = pchip(timeAltitude(:,1, starname_i), ....
            %         timeAltitude(:,4, starname_i), ...
            %         xts);
            %     e_density_inv = 1./(G*mass_i^2./(8*pi*(distances_km*1E3).^4))  ;
            % 
            %     minpp = min((e_density_inv));
            %     maxpp = max((e_density_inv));
            % 
            %     % normalize and scale to -90:90              
            %     e_density_inv_norm = (e_density_inv - minpp) / (maxpp-minpp)*40-20;
            % 
            %     x = xts;
            %     y = e_density_inv_norm;
            % 
            % end
        end
        plot_handles(starname_i) = plot(x, y, '.', ...
            'Color', colors{starname_i}, ...
            'LineStyle', '-', ...
            'LineWidth', 3);
    end
    legend(plot_handles, stars); % Use plot handles in legend
    yyaxis left
    if holdStatus
        hold on
    end
end