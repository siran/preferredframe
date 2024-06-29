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

    get_star_info
    
    plot_handles = gobjects(size(timeAltitude,3), 1); % Preallocate handles

    for starname_i = 1:numel(star_info.stars)
        starname = star_info.stars{starname_i};
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
            'Color', star_info.colors{starname_i}, ...
            'LineStyle', star_info.linestyles{starname_i}, ...
            'LineWidth', 1, ...
            'Marker', star_info.markers{starname_i});
    end
    legend(plot_handles, star_info.stars); % Use plot handles in legend
    yyaxis left
    if holdStatus
        hold on
    end
end