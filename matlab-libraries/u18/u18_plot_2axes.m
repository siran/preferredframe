x=[1 2 3]
y = [1 2 3]
plot(x,y)
ax1 = gca
ax1_pos = get(ax1,'Position')
ax2 = axes('Position',ax1_pos,...
'XAxisLocation','top',...
'YAxisLocation','right',...
'Color','none');

hold on

plot(ax2, x.^2,y.^2)