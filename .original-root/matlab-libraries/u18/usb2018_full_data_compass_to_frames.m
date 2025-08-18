tm=xts;
azimuthvar = orientacion;
[rotation_pks,rotation_locs]=findpeaks(sin(azimuthvar/360*2*pi),'minpeakdistance',40);
fprintf('%d picos de rotacion encontrados. \n', size(rotation_pks,1));
if ~exist('graficoAzimuth') || graficoAzimuth == true
    figure
    oh = hampel(azimuthvar(10:length(azimuthvar)));
    plot(oh, 'b.-')
%     ylim([-2 2])
    hold on

%     plot(rotation_locs, rotation_pks, 'o')
%     line([rotation_locs rotation_locs], ylim,'color', 'r')
    title('Compass angle vs # photo')
    xlabel('# foto')
    ylabel('Compass angle (º)')
    legend('Angle of rotation', 'Rotation indicators')
    usb2018_saveFigureToFile('rotaciones-separadas')
end


if (exist('ajustarDefault') && ajustarDefault ~= true) || ~exist('ajustarDefault')
    ajustar = input('desea unificar en una linea la data? [s]/n: ', 's');
end

if (exist('ajustar') && (isempty('ajustar') || strcmp(ajustar, 's'))) || (exist('ajustarDefault') && ajustarDefault == true)
    p_adjusted = usb2018_adjustdata();
%     p_adjusted = usb2018_adjustdata(p_orig);
    p = p_adjusted;
    padj = p_adjusted;
end    


% if exist('azimuthvar')
%     maxp = max(max(p));
%     seriesToPlot = azimuthvar;
%     dataToPlot = (seriesToPlot-mean(seriesToPlot))/(max(seriesToPlot)-mean(seriesToPlot))*maxp/4;
% end

figure
usb2018_grafico_max_hip54217
% figure
% plot(p,'.')
% xlabel('# photo')
% ylabel('Position of Interference Maximum (px)')
% title('Position of Interference Maximum (px) vs # photo')
% xlim([0 size(p,1)])

% if exist('locs')
%     line([tm(locs) tm(locs)], ylim,'color', 'k', 'linewidth', 2)
% end   


% datetick('x','dd/mm HH:MM','keepticks')
usb2018_saveFigureToFile('franjas')
