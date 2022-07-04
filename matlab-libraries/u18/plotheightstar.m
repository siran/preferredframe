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
    ylabel('Altitude of star (°, blue line)')

    if ax.XLim == [0 360]
        altitudes = pchip(timeAltitude(:,1), timeAltitude(:,2), ...
            xts(1):(xts(end)-xts(1))/360:xts(end));

        azimuths = pchip(timeAltitude(:,1), timeAltitude(:,3), ...
            xts(1):(xts(end)-xts(1))/20:xts(end));
        
        plot(0:360, altitudes, 'b-', 'lineWidth', 3)
        plot(azimuths, vertical_steps,'b-', 'lineWidth', 3)                  
    else
        plot(timeAltitude(:,1),timeAltitude(:,2),'b.-','lineWidth',3)
    end
    yyaxis left
    if holdStatus
        hold on
    end
end