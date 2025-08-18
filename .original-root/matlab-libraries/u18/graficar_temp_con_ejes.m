tm=x2mdate(tt);

temps=temp;
% temps=smooth(temp,40);
ax1 = gca;

mint = min(temps);
maxt = max(temps);
dift = maxt-mint;

scale=1.02;
heightOfGraph = diff(get(gca,'YLim'))*scale

h = axes('Visible','on',  'YAxisLocation','right', 'Color', 'none','YLim',[mint/scale maxt*scale])

hold on
plot(tm,temps,'.-','linewidth', 1,'color','red');
set(gca,'XLim', [startDate endDate+1/2])
set(gca,'XTick',startDate:12/24:endDate+1/2)
set(gca,'XMinorTick','on')
set(gca,'Box','off');
datetick('x','dd/mm HH:MM','keepticks')
legend('temperatura', 'NorthEast')
% set('Position',get(ax1,'Position'),'Visible','on',  'YAxisLocation','right', 'Color', 'none','YLim',[mint/scale maxt*scale])
% ylim([mint maxt]);

% plot(tm,temps,'.--');

% if exist('startDate'); mintm = startDate; else  mintm = min(tm); end
% if exist('endDate'); maxtm = endDate; else maxtm = max(tm); end

% difft = (max(temps)-min(temps))/10;

% set(gca,'XLim', [mintm maxtm+15/24]);
% set(gca,'XTick', mintm:12/24:maxtm+12/24)
% set(gca,'YLim', [min(temps)-difft max(temps)+difft])

% title('Temperatura (ºC) vs. tiempo)');
% datetick('x','dd/mm HH:MM','keepticks');


% temps=smooth(temps,500);
% plot(tm,-heightOfGraph*(temps-min(temps))/max(temps-min(temps))+heightOfGraph,'*-','linewidth', 1,'color','green')

% 
% ax2 = axes('Position',get(ax1,'Position'),...
% 'Color','none',...
% 'XColor','k','YColor','k','XTick',-1,...
% 'YAxisLocation','right',...
% 'YLim',[mint maxt]);
% xlim([min(x_timestamp) max(x_timestamp)+1/2]);


% 'YDir', 'reverse'
% 'YTick',[roundn(min(temps),-2):.05:roundn(max(temps),-2)],...



% plot(tm,350*(temp-min(temp))/max(temp-min(temp))  ,'x-','linewidth',
% 1,'color','blue')



