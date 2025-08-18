hold off

if exist('tt') & exist('azimuthvar')
    fprintf('\n\n ya existen variables tt (%d filas) y azitmuth (%d filas) \n\n', size(tt,1), size(azimuthvar,1))
end

if (exist('ajustarDefault') && ajustarDefault ~= true) || ~exist('ajustarDefault')
    ajustar = input('desea importar tempertura? [s]/n: ', 's');
end

if (exist('ajustar') && isempty(ajustar)) || (exist('ajustarDefault') && ajustarDefault == true) || (exist('ajustar') && strcmp(ajustar,'s'))
        if exist('pathToVideo')
            fullDataFile = [pathToVideo 'full_data_compass_' videoId '.txt'];
        else
            fprintf('\n\n no existe pathToVideo ejecute primero "videorobertNN" \n\n');
            break
        end    
        fprintf('Importando datos de la brujula ... \n')
        [tt,azimuthvar,temp,magneticscalar,magneticx,magnetict,magneticz,accelerationscalar,accelerationx,accelerationy,accelerationz,lifecount] ...
            = import_raw_full_data_compass(fullDataFile);

%         tm = x2mdate(tt);

        

        temp_orig = temp;
        tm = tt;
        
        azimuth_orig = azimuthvar;
        
        azimuthvar(azimuthvar>300)=azimuthvar(azimuthvar>300)-360;
        
        fprintf('%d filas importadas. \n', size(tt,1));
        
        [pks,locs]=findpeaks(azimuthvar,'minpeakdistance',300, 'MINPEAKHEIGHT',0);
        fprintf('%d picos de rotacion encontrados. \n', size(pks,1));       
end

if exist('azimuthvar')
        [pks,locs]=findpeaks(azimuthvar,'minpeakdistance',300, 'MINPEAKHEIGHT',0);
        fprintf('%d picos de rotacion encontrados. \n', size(pks,1));
        if ~exist('graficoAzimuth') || graficoAzimuth == true
            figure
            plot(1:length(azimuthvar),azimuthvar,'b-')
            line([locs locs], ylim,'color', 'r')
            title('Rotations of Interferometer')
            saveFigureToFile('rotaciones-separadas')
        end
end

if (exist('ajustarDefault') && ajustarDefault ~= true) || ~exist('ajustarDefault')
    ajustar = input('desea unificar en una linea la data? [s]/n: ', 's');
end

if (exist('ajustar') && (isempty('ajustar') || strcmp(ajustar, 's'))) || (exist('ajustarDefault') && ajustarDefault == true)
    p_adjusted = adjustdata(p_orig);
    p = p_adjusted;
end    


% if exist('azimuthvar')
%     maxp = max(max(p));
%     seriesToPlot = azimuthvar;
%     dataToPlot = (seriesToPlot-mean(seriesToPlot))/(max(seriesToPlot)-mean(seriesToPlot))*maxp/4;
% end

figure
plot(xts,p,'.')

if exist('locs')
    line([tm(locs) tm(locs)], ylim,'color', 'k', 'linewidth', 2)
end   


datetick('x','dd/mm HH:MM','keepticks')
saveFigureToFile('franjas')


% if exist('videoId') & exist('tt') & exist('azimuthvar') & exist(fullDataFile)
% 
%         frameAzimuth = nan(size(tt,1),2);
%         t0 = tt(2);
%         for timePoint=2:size(tt,1)
%            frame = round((tt(timePoint) - t0)*24*60*60 * fps) + 1;
%            frameAzimuth(timePoint, :) = [frame azimuthvar(timePoint)];
%            fprintf('%d \n ', timePoint);
%         end
% 
% else
%     fprintf('fullDataFile, videoId, tt or azimuth not found');
% end