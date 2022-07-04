% figure
fprintf('%s','Graficando...\n');
startDate = min(x_timestamp);%datenum(files_images(1).date);
endDate = max(x_timestamp);%datenum(files_images(size(p,1)).date);
% xData = linspace(startDate,endDate,size(p,1));

plot(x_timestamp, p,'.',...
    'markersize', 5 ...
)
% hold on
% plot(x_timestamp, p(:,11), 'x', 'markersize', 6)

grid off

% set(gca,'Position', [0.05 0.05 0.93 0.88])
% set(gca,'XLim', [startDate endDate])
% set(gca,'XTick',startDate:endDate)
% set(gca,'XMinorTick','on')
% set(gca,'Box','off');
datetick('x','dd/mm HH:MM','keepticks')



 
t = title(['Movement of Interference Maxima: from ' datestr(x_timestamp(1)) ' to ' datestr(x_timestamp(size(p,1)))],'FontSize', 16);
titleposition = get(t,'Position');

xlabel('Time (HH:MM)');
ylabel('Position of Maxima (pixels)');

% lineasestelares
hold off