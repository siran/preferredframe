function [XX, YY] = divideInChunks(x, y, rotation0_locs, numpoints, orientacion)
% divideInChunks(Y, divisions, numpoints)
% returns a matrix `chunks` dividing vector Y by its indices `divisions` 
% and does a numpoints interporlation


XX = [];
YY = [];

i = 0;
rotacionini=2;
% if ~exist('rotacionini')
%     rotacionini = 6;
% end
rotacionfin = length(rotation0_locs );

numrotaciones = rotacionfin - rotacionini;

% se separa cada rotacion
% luego se interpola cada rotacion con 360 puntos
for k=rotacionini:rotacionfin
    i = i+1;
%     rango = rotation0_locs(k-1):1/24/60*3:rotation0_locs(k);
    
    inicio = rotation0_locs(k-1);
    fin = rotation0_locs(k);
%     inicioFecha = 
    pasos = (fin-inicio)/numpoints;
%     pasosFechas=
%     XX(i,:) = inicio:pasos:fin-pasos;
%     fechas(i,:) = inicio:pasos:fin-pasos

%     plot( ...
%          xts(xts>tm(rotation0_locs(k-1)) & xts<tm(rotation0_locs(k))), ...
%         y(xts>tm(rotation0_locs(k-1)) & xts<tm(rotation0_locs(k))), ...
%         'color', colors{mod(k,5)+1} ...
%     );

%     try
        xx = inicio:pasos:fin-pasos;
        xlocs = x>=rotation0_locs(k-1) & x<rotation0_locs(k);
        if isnan(y(xlocs))
            break
        end
        YY(i,:) = pchip( ...
            x(xlocs), ...
            y(xlocs), ...
            xx ...
        );
        XX(i,:) = pchip( ...
            x(xlocs), ...
            x(xlocs), ...
            xx ...
        );
        legends{i} = int2str(k);
%     catch
%         nada=1;
%     end
end

if ~isempty(YY)
    YY = hampel(YY);
end

fin=1;
% chunks = [XX YY];