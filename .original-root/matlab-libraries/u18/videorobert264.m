clear p x_timestamp xts ps peaks locs p_orig x_timestamp_orig perfiles lineaPreferida puntosSuavizadoPreferido tt azimuth

animar = false

global videoId
global pathToFigures
global saveFile
global frameToTime

videoId = 'M2U00264';
pathToVideo = 'C:\Users\an\Documents\fisica\michelson-morley\robert\150101 - maraton enero\';
pathToFigures = 'C:\Users\an\Dropbox\fisica\interferometro 1way USB\figures\';
saveFile = true;

% 3:29pm al minuto 1:50.858, frame 3325
% 3:29 30s al minuto 2:20.763, frame 4221
% 3:30     al minuto 2:50.885, frame 5124
% 3:30 30s al minuto 3:20.64, frame
frameToTime = [1867 datenum('02-jan-2015 17:40:00')];


xyloObj = VideoReader([pathToVideo videoId '.avi']);

% nFrames = xyloObj.NumberOfFrames
% vidHeight = xyloObj.Height
% vidWidth = xyloObj.Width
fps = xyloObj.FrameRate;

maxfiles = xyloObj.NumberOfFrames;

% configuracion de visualizacion
stepFrames = 30;
% puntosSuavizadoPreferido = 40;
ajustarDefault = true;
saveLogFile('init')

lineaPreferida = 9  ;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% p = nan(maxfiles(1),20);
% x_timestamp = zeros(maxfiles(1),1);

t=0;
tini=tic;
% frame 15103 corresponde a las 5:57pm del 20/09/2007
fila=0;
for i=1:stepFrames:maxfiles
    if i<2006
        continue
    end
    fila = fila +1;
%     if ~(mod(i,round(30*fps))==0)
%         p(i,:) = nan;
%         continue
%     end
    if ~exist('lastI') | (mod((i - lastI),200)==0)
        elapsed = toc(tini)/60;
        total = (maxfiles(1)*elapsed/i);
        faltante = (total-elapsed);
        if ((total-elapsed) < 1)
            faltante = (total-elapsed)*60;
        end
        fprintf('%d/%d - %6.1f - total est.: %4.2f min, transcurridos: %4.2f min, faltante: %4.2f min \n', i, maxfiles(1), round(i/maxfiles(1)*10000)/100, total, elapsed, faltante);
        lastI = i;
    end    
    if (i>=3225)
            a=1;
    end
    x_timestamp(fila) = datenum(frameToTime(1,2))-((frameToTime(1,1)-i)/fps/24/60/60);
    
    
    
    imagen = read(xyloObj, i);

    imagen = rgb2gray(imagen);
    imagen = imadjust(imagen);
    imagen = imrotate(imagen, -10);     
    imagen = imfilter(imagen,fspecial('gaussian',20,10));
      
        perfil = imagen(250, 343:633);
    perfil = double(perfil);
    perfil=smooth(perfil);
% 
    perf = perfil;
%     show = round(maxfiles/20);
%     if (mod(i,show(1,1))==0)
%         figure;
%         plot(perfil)
%         a=2
%     end     
%     xd = 1:size(perfil);
%     [curve, goodness] = fit(xd', perfil, 'sin8');
%     perfil = double(curve(1:size(perfil)));
    clear locs peaks;
    cuentaPicos = 0;
%     locs(cuentaPicos) = 0;
    distanciaEntrePicos = 15;
    for k=2+distanciaEntrePicos:size(perfil)-1-distanciaEntrePicos
        if perfil(k)>=perfil(k-1) && perfil(k)>=perfil(k+1)
            if (perfil(k) >= max(perfil(k-distanciaEntrePicos:k+distanciaEntrePicos)) ) %&& k-locs(cuentaPicos)>distanciaEntrePicos
                cuentaPicos = cuentaPicos + 1;
                locs(cuentaPicos) = k;
                peaks(cuentaPicos) = perfil(k);
            end
%             fprintf('%4d ', locs(size(locs, 2)));
        end
    end
%      fprintf('\n');
    
    perfil=perf;
    perfiles(fila,:,:) = perfil;
    
    if exist('animar') & animar == true
        plot(perfil)
        hold on
        plot(locs,peaks,'o')    
        hold off
        drawnow;
    end
    
    p(fila,1:cuentaPicos) = locs;
end

% filter out repeated times
% [x_timestamp,Ix_timestamp_orig,Ix_timestamp] = unique(x_timestamp);
% p(Ix_timestamp, :) = [];

if ~exist('p_orig')
    p_orig = p;
end
if ~exist('x_timestamp_orig') && exist('x_timestamp')
    x_timestamp_orig = x_timestamp;
end

xts = x_timestamp';

full_data_compass_to_frames
findbettercol
separarrotaciones
