clear p x_timestamp xts ps peaks locs p_orig x_timestamp_orig perfiles lineaPreferida puntosSuavizadoPreferido tt azimuth

animar = false

global pathToFigures
global saveFile
global frameToTime
global xts
global p_orig
global videoId

videoId = '180820_conrotacion'

lineaPreferida=7
suavizar=true
stepFrames = 1;
ajustarDefault = true
% saveLogFile('init')
graficoAzimuth = true
limitesGraficasPromediada = false   
rotacionini = 1

pathToFigures = 'C:\Users\an\Documents\megasync-preferredframe\figures\';
saveFile = true;

path_images = 'C:\Users\an\Documents\megasync-preferredframe\180820\con-rotacion\';

fprintf('Procesando directorio %s \n\n', path_images );

if (~exist('files_images'))
    % leo archivos
    files_images = dir(strcat(path_images,'*.jpg'));

    % ordeno por fecha
    for t=1:size(files_images)
        files_images(t).datenum = mat2str(datenum(files_images(t).date));
    end
    [tmp ind]=sort({files_images.datenum});
    files_images = files_images(ind);
end

maxfiles = size(files_images, 1);
   
p = nan(maxfiles(1),20);
orientacion = zeros(maxfiles(1),1);
x_timestamp = zeros(maxfiles(1),1);

t=0;
tini=tic;
fila=0;
warning('off', 'MATLAB:imagesci:tifftagsread:expectedTagDataFormat')
for i=1:stepFrames:maxfiles
    fila = fila +1;
    name_image = files_images(i).name;    
    full_name_image = strcat(path_images, name_image);
    x_timestamp(i) = datenum(files_images(i).date);
    exifinfo = imfinfo(full_name_image);
    orientacion(i) = exifinfo.GPSInfo.GPSImgDirection;
%     [a, MSGID] = lastwarn()
%     if orientacion(i) 
     
    if ~exist('lastI') || (mod((i - lastI),100)==0)
        elapsed = toc(tini)/60;
        total = (maxfiles(1)*elapsed/i);
        faltante = (total-elapsed);
        if ((total-elapsed) < 1)
            faltante = (total-elapsed)*60;
        end
        fprintf('%d/%d - %6.1f - total est.: %4.2f min, transcurridos: %4.2f min, faltante: %4.2f min \n', i, maxfiles(1), round(i/maxfiles(1)*10000)/100, total, elapsed, faltante);
        lastI = i;
    end    
%     if (i>=3225)
%             a=1;
%     end
    
    [imagen map]= imread(full_name_image);
     imagen = rgb2gray(imagen);
     imagen = imadjust(imagen);
     imagen = imrotate(imagen, 35);     
    imagen = imfilter(imagen,fspecial('disk', 20));
      
    y=520;
    perfil = imagen(y,:);
    perfil = double(perfil);
    perfil=smooth(perfil);    
    if ~exist('figureCreated')
        imshow(imagen)
        hold on
        line([0 1000],[y y], 'color', 'r')
        usb2018_saveFigureToFile('row_intensity_profile')
        
        hold off
        figure
        plot(perfil)
        xlabel('Pixel #')
        ylabel('Intensity')
        usb2018_saveFigureToFile('intensity_profile')
        figureCreated = true;
    end 
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
    [peaks,locs] = findpeaks(perfil, 'MinPeakDistance',30);  
%     for k=2+distanciaEntrePicos:size(perfil)-1-distanciaEntrePicos
%         if perfil(k)>=perfil(k-1) && perfil(k)>=perfil(k+1)
%             if (perfil(k) >= max(perfil(k-distanciaEntrePicos:k+distanciaEntrePicos)) ) %&& k-locs(cuentaPicos)>distanciaEntrePicos
%                 cuentaPicos = cuentaPicos + 1;
%                 locs(cuentaPicos) = k;
%                 peaks(cuentaPicos) = perfil(k);
%             end
% %             fprintf('%4d ', locs(size(locs, 2)));
%         end
%     end
%      fprintf('\n');
    
    perfil=perf;
    perfiles(fila,:,:) = perfil;
    
%     if exist('animar') & animar == true
%         plot(perfil)
%         hold on
%         plot(locs,peaks,'o')    
%         hold off
%         drawnow;
%     end
    if size(locs,2) < 2
        bs=1;
    end
    p(fila,1:size(locs,1)) = locs;
end

% filter out repeated times
% [x_timestamp,Ix_timestamp_orig,Ix_timestamp] = unique(x_timestamp);
% p(Ix_timestamp, :) = [];

% if ~exist('p_orig') || isempty(p_orig)
    p_orig = p;
% end
% if ~exist('x_timestamp_orig') && exist('x_timestamp')
    x_timestamp_orig = x_timestamp;
% end

xts = x_timestamp_orig';

usb2018_grafico_max_hip54217
usb2018_full_data_compass_to_frames
usb2018_findbettercol
% separarrotaciones
