% plot height of star
if exist('timeAltitude') && ~isempty(timeAltitude)
    holdStatus = ishold;
    hold on
    ax = gca;
    height = diff(ax.YLim);
    yyaxis right
    ax.YColor = [0 0 0];
    ylimites = [-90 90];
    ylim(ylimites)

    ax = gca;
    ax.YTick = [-90 -80:20:80 90];

    vertical_steps = -90:180/20:90;
    ylabel('Altitude of stellar objects')

    if ax.XLim == [0 360]
        colors = {'b', 'y', 'k'};
        stars = {'HIP54589', 'Sun', 'Moon'};
        plot_handles = gobjects(size(timeAltitude,3), 1); % Preallocate handles

        for starname_i = 1:numel(stars)
            altitudes = pchip(timeAltitude(:,1, starname_i), timeAltitude(:,2, starname_i), ...
                xts(1):(xts(end)-xts(1))/360:xts(end));

            azimuths = pchip(timeAltitude(:,1, starname_i), timeAltitude(:,3, starname_i), ...
                xts(1):(xts(end)-xts(1))/20:xts(end));

            plot_handles(starname_i) = plot(0:360, altitudes, [colors{starname_i} '.-'], 'lineWidth', 3);
            hold on; % Hold the plot to add multiple lines to the same plot
            plot(azimuths, vertical_steps, [colors{starname_i} '.-'], 'lineWidth', 3);
        end

        legend(plot_handles, stars);% Use plot handles in legend

    else
        colors = {'b', 'y', 'k'};
        stars = {'HIP54589', 'Sun', 'Moon'};
        plot_handles = gobjects(size(timeAltitude,3), 1); % Preallocate handles

        for starname_i = 1:size(timeAltitude, 3)
            plot_handles(starname_i) = plot(timeAltitude(:, 1, starname_i), timeAltitude(:, 2, starname_i), ...
                [colors{starname_i} '.-'], 'lineWidth', 3);
        end

        legend(plot_handles, stars); % Use plot handles in legend
    end
    % legend([{'Fringe shift'}, stars])
    yyaxis left
    if holdStatus
        hold on
    end
end