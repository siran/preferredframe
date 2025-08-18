% configure common options for plots

set(gca, 'XTickMode', 'auto', 'XTickLabelMode', 'auto')
if exist('x_start', 'var') && exist('x_end', 'var')
    xlim([x_start x_end])
end

xlabel('Time');
set(gca,'XMinorTick','on')
datetick('x', 'dd/mm HH:MM','keeplimits')
ax = gca;
% ax.XTickLabelRotation = 90;