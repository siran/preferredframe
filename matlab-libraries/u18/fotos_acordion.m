clear p x_timestamp xts ps peaks locs p_orig x_timestamp_orig perfiles lineaPreferida puntosSuavizadoPreferido tt azimuth

animar = false

global videoId
global pathToFigures
global saveFile
global frameToTime

videoId = 'IMG_20151206_130019';
pathToVideo = 'C:\Users\an\Desktop\double-pinhole\';
pathToFigures = 'C:\Users\an\Dropbox\fisica\interferometro 1way USB\figures\';

% 3:29pm al minuto 1:50.858, frame 3325
% 3:29 30s al minuto 2:20.763, frame 4221
% 3:30     al minuto 2:50.885, frame 5124
% 3:30 30s al minuto 3:20.64, frame
frameToTime = [1433 datenum('13-jul-2015 23:00:00')];


imagen = imread([pathToVideo videoId '.jpg']);

    imagen = rgb2gray(imagen);
%     imagen = imadjust(imagen);
%     imagen = imrotate(imagen, 0);     
%     imagen = imfilter(imagen,fspecial('gaussian',10,5));
      
        perfil = imagen(860, 92:1530);
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
    if size(locs,2) < 2
        bs=1;
    end
    p(fila,1:cuentaPicos) = locs;



