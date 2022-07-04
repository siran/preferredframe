clear p x_timestamp xts ps peaks locs p_orig x_timestamp_orig perfiles lineaPreferida puntosSuavizadoPreferido tt azimuth

warning('off', 'MATLAB:imagesci:tifftagsread:expectedTagDataFormat')
warning('off', 'images:initSize:adjustingMag')
warning('off', 'MATLAB:audiovideo:VideoWriter:noFramesWritten')

animar = false;

global pathToFigures
global saveFile
global frameToTime
global xts
global p_orig
global videoId

path_images = 'C:\Users\an\Documents\megasync-preferredframe\180820\con-rotacion\';
videoId = 'w180820_conrotacion'

lineaPreferida=5;
lineaPreferidaAdjunta=6;


suavizar=false;
stepFrames = 1;
ajustarDefault = true;
% saveLogFile('init')
graficoAzimuth = true;
limitesGraficasPromediada = false;
rotacionini = 1;
rotationAngle = 35;
filterDiskSize = 20;

pathToFigures = 'C:\Users\an\Documents\megasync-preferredframe\figures\';
saveFile = true;
figureCreated = false;

if exist('onlyLoadConfig') && onlyLoadConfig == true
    return
end

u18_analisis_fotos
% 
% fprintf('Procesando directorio %s \n\n', path_images );
% 
% if (~exist('files_images'))
%     % leo archivos
%     files_images = dir(strcat(path_images,'*.jpg'));
% 
%     % ordeno por fecha
%     for t=1:size(files_images)
%         files_images(t).datenum = mat2str(datenum(files_images(t).date));
%     end
%     [tmp ind]=sort({files_images.datenum});
%     files_images = files_images(ind);
% end
% 
% maxfiles = size(files_images, 1);
%    
% p = nan(maxfiles(1),20);
% orientacion = zeros(maxfiles(1),1);
% x_timestamp = zeros(maxfiles(1),1);
% 
% t=0;
% tini=tic;
% fila=0;
% warning('off', 'MATLAB:imagesci:tifftagsread:expectedTagDataFormat')
% for i=1:stepFrames:maxfiles
%     fila = fila +1;
%     name_image = files_images(i).name;    
%     full_name_image = strcat(path_images, name_image);
%     x_timestamp(i) = datenum(files_images(i).date);
%     exifinfo = imfinfo(full_name_image);
%     orientacion(i) = exifinfo.GPSInfo.GPSImgDirection;
% %     [a, MSGID] = lastwarn()
% %     if orientacion(i) 
%      
%     if ~exist('lastI') || (mod((i - lastI),100)==0)
%         elapsed = toc(tini)/60;
%         total = (maxfiles(1)*elapsed/i);
%         faltante = (total-elapsed);
%         if ((total-elapsed) < 1)
%             faltante = (total-elapsed)*60;
%         end
%         fprintf('%d/%d - %6.1f - total est.: %4.2f min, transcurridos: %4.2f min, faltante: %4.2f min \n', i, maxfiles(1), round(i/maxfiles(1)*10000)/100, total, elapsed, faltante);
%         lastI = i;
%     end    
% %     if (i>=3225)
% %             a=1;
% %     end
%     
%     [imagen map]= imread(full_name_image);
%      imagen = rgb2gray(imagen);
%      imagen = imadjust(imagen);
%      imagen = imrotate(imagen, rotationAngle);     
%     imagen = imfilter(imagen,fspecial('disk', filterDiskSize));
%       
%     y=520;
% %     perfil = imagen(y,:);
%     perfil = mean(imagen);
%     perfil = double(perfil);
%     perfil=smooth(perfil);    
%     if ~exist('figureCreated') || figureCreated==false
%         imshow(imread(full_name_image))
%         axis on
%         xlabel('Width of original image (px)')
%         ylabel('Height of original image (px)')
%         title('First image of session (original)')
%         usb2018_saveFigureToFile('original_image')
%         
%         figure
%         imshow(imagen)
%         axis on
%         hold on
% %         line([0 1000],[y y], 'color', 'r')
%         plot(-1*perfil*round(size(imagen,1)/max(max(perfil))/5)+round(size(imagen,1)/3*2), 'color','r', 'linewidth',2)
%         legend('Smoothed mean of rows')
%         xlabel('Width of rotated image (px)')
%         ylabel('Height of rotated image (px)')
%         title('First image of session (original) after rotation, B&W and adjust')
%         usb2018_saveFigureToFile('intensity_profiles')
%         
%         hold off
%         figure
%         plot(perfil)
%         xlabel('Pixel #')
%         ylabel('Intensity (0=black, 255=white)')
%         title({'Smoothed mean of all intensity profiles (rows) of image'})
%         usb2018_saveFigureToFile('intensity_profile')
%         figureCreated = true;
% %         return
%     end
% % 
%     perf = perfil;
% %     show = round(maxfiles/20);
% %     if (mod(i,show(1,1))==0)
% %         figure;
% %         plot(perfil)
% %         a=2
% %     end     
% %     xd = 1:size(perfil);
% %     [curve, goodness] = fit(xd', perfil, 'sin8');
% %     perfil = double(curve(1:size(perfil)));
%     clear locs peaks;
%     cuentaPicos = 0;
% %     locs(cuentaPicos) = 0;
%     distanciaEntrePicos = 15;
%     [peaks,locs] = findpeaks(perfil, 'MinPeakDistance',30);  
% %     for k=2+distanciaEntrePicos:size(perfil)-1-distanciaEntrePicos
% %         if perfil(k)>=perfil(k-1) && perfil(k)>=perfil(k+1)
% %             if (perfil(k) >= max(perfil(k-distanciaEntrePicos:k+distanciaEntrePicos)) ) %&& k-locs(cuentaPicos)>distanciaEntrePicos
% %                 cuentaPicos = cuentaPicos + 1;
% %                 locs(cuentaPicos) = k;
% %                 peaks(cuentaPicos) = perfil(k);
% %             end
% % %             fprintf('%4d ', locs(size(locs, 2)));
% %         end
% %     end
% %      fprintf('\n');
%     
%     perfil=perf;
%     perfiles(fila,:,:) = perfil;
%     
% %     if exist('animar') & animar == true
% %         plot(perfil)
% %         hold on
% %         plot(locs,peaks,'o')    
% %         hold off
% %         drawnow;
% %     end
%     if size(locs,2) < 2
%         bs=1;
%     end
%     p(fila,1:size(locs,1)) = locs;
% end
% 
% % filter out repeated times
% % [x_timestamp,Ix_timestamp_orig,Ix_timestamp] = unique(x_timestamp);
% % p(Ix_timestamp, :) = [];
% 
% % if ~exist('p_orig') || isempty(p_orig)
%     p_orig = p;
% % end
% % if ~exist('x_timestamp_orig') && exist('x_timestamp')
%     x_timestamp_orig = x_timestamp;
% % end
% 
% xts = x_timestamp';
% 
% % usb2018_grafico_max_hip54217
% % usb2018_full_data_compass_to_frames
% % usb2018_findbettercol
% % separarrotaciones
