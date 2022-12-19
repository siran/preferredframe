% Determine the maxima of an interference pattern
% From all pictures in a folder

warning('off', 'MATLAB:imagesci:tifftagsread:expectedTagDataFormat')
wspath = 'D:\Users\an\experimento-usb-interferometro\u18_workspaces\';

mkdir([path_images '\ignored_images'])

minpeakdistance = 30;
if isfield(processing_session, 'minpeakdistance') && ~isempty(processing_session.minpeakdistance)
    minpeakdistance = processing_session.minpeakdistance;
end

smooth_num_points = 20;
if isfield(processing_session, 'minpeakdistance') && ~isempty(processing_session.minpeakdistance)
    smooth_num_points = processing_session.smooth_num_points;
end

filterDiskSize = 5;
if isfield(processing_session, 'filterDiskSize') && ~isempty(processing_session.filterDiskSize)
    filterDiskSize = processing_session.filterDiskSize;
end

if isfield(processing_session, 'rotating_session') && ~isempty(processing_session.filterDiskSize)
    rotating_session = processing_session.rotating_session;
end

fprintf('Procesando directorio: %s \n\n', session );
fprintf('Scanning goodness of files...\n')

% scan goodness of files
restart = false;

if (~exist('files_images', 'var'))   
    % leo archivos
    files_images_raw = dir(strcat(path_images,'*.jpg'));
    maxfiles = length(files_images_raw);
    
    if maxfiles < 100
        fprintf('Muy pocos archivos: %d, videoid: %s\n', maxfiles, videoId)
        return
    end
    
    stepFrames=1;

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %% ordeno por fecha
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    image_counter = 0;
    for t=1:size(files_images_raw)
        full_name_image = [path_images files_images_raw(t).name];

        name_image = files_images_raw(t).name;
        if isequal(exist([path_images '\ignored_images\' name_image ],'file'),2)
            fprintf('Ignoring file %s\n', name_image)
            continue
        end
        

        
        image_counter = image_counter+1;
        try
            if t==1
                files_images_raw = dir(strcat(path_images,'*.jpg'));
                info1 = imfinfo([path_images files_images_raw(1).name]);
                info2 = imfinfo([path_images files_images_raw(2).name]);
                info3 = imfinfo([path_images files_images_raw(3).name]);

                % sometimes the first image is rotated 90degress which causes the program
                % to error out
                if info1.Width ~=info2.Width && info1.Width ~=info3.Width
                    copyfile([path_images files_images_raw(1).name], [path_images 'ignored_images'])
                end
            end

            info = imfinfo([path_images files_images_raw(t).name]);
            date = info.DigitalCamera.DateTimeOriginal;
            files_images(image_counter) = files_images_raw(t);
            files_images(image_counter).datenum = datenum(date,'yyyy:mm:dd HH:MM:SS');
            x_timestamp(image_counter) = files_images(image_counter).datenum;
            orientacion(image_counter) = info.GPSInfo.GPSImgDirection;
        catch
            fprintf('Invalid file %s, renaming... \n', full_name_image)
%             delete(full_name_image)
            movefile(full_name_image, [full_name_image '-invalid'])
            restart = true
            continue
        end
        
    end
    orientacion_orig = orientacion;
    [tmp, ind]=sort([files_images.datenum]);
    files_images = files_images(ind);
    x_timestamp = x_timestamp(ind);
end

maxfile = length(files_images);

% restarting if files were deleted
if restart
    new_date_start = datestr(session_datenum,'yyyy-mm-dd HH:MM');
    fprintf('Setting date_start from %s to %s\n', date_start, new_date_start)
    date_start = new_date_start
    clearvars -except session processing_session date_start date_end day_session session_datenum
    fprintf('Restarting\n')
    u18w_general
    return
end

p = nan(length(files_images),20);
%     orientacion = nan(length(1:stepFrames:maxfiles), 1 );
%     x_timestamp = nan(length(1:stepFrames:maxfiles), 1 );

% [rotation0_pks,rotation0_locs] = findpeaks(sin(orientacion/360*2*pi + pi/2),                                           'MinPeakHeight', 0.95);
% [rotation0_pks,rotation0_locs] = findpeaks(sin(orientacion/360*2*pi + pi/2),x_timestamp,'minpeakdistance',1/24/60*2.5, 'MinPeakHeight', 0.95);

invalid_elements = find(diff(x_timestamp)<=0,1,'first');
if ~isempty(invalid_elements)
    invalid_index = invalid_elements(1);
    x_timestamp(invalid_index+1) = (x_timestamp(invalid_index) + ...
        x_timestamp(invalid_index+2))/2;
end
[rotation0_pks,rotation0_locs] = findpeaks(sin(orientacion/360*2*pi + pi/2),x_timestamp);

num_rotations = length(rotation0_pks);

if num_rotations < 5
    if exist('rotating_session', 'var') && ~isempty(rotating_session) || ~exist('rotating_session', 'var')
        fprintf('Not enough rotations %s\n', videoId)
        ignore_folder = true;
        return
    end
end
 
% orientacion = zeros(maxfiles(1),1);
% x_timestamp = zeros(maxfiles(1),1);

t=0;
tini=tic;
fila=0;
warning('off', 'MATLAB:imagesci:tifftagsread:expectedTagDataFormat')


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Determine angle of rotation
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

clear sum_image max_sum_image num_im_peaks rotationAngle

name_image = files_images(1).name;
full_name_image = strcat(path_images, name_image);
[imagen, map]= imread(full_name_image);
imagen = rgb2gray(imagen);
imagen = imadjust(imagen);
imagen = imfilter(imagen,fspecial('disk', filterDiskSize));

% 1. sum the image for every angle
angulos = 0:95;
a=0;
indice =0;
for angulo=angulos
    a = a + 1;
    rotated_image = imrotate(imagen, angulo);
    perfil = smooth(double(sum(rotated_image)), smooth_num_points);
    [peaks,locs] = findpeaks(perfil, 'MinPeakDistance',minpeakdistance,'MinPeakProminence',1e3); 

    if length(peaks) > 3
        num_peaks(a) = length(peaks);
        max_sum_image(a) = max(sum(perfil));
        
%         %%% visualize peaks and rotation
%         subplot(1,3,1)
%         hold off
%         plot(perfil)
%         hold on
%         plot(locs, peaks,'o')
%         title(int2str(angulo))
%         subplot(1,3,2)
%         hold off
%         plot(hampel(max_sum_image),'o')
%         subplot(1,3,3)
%         hold off
%         imshow(rotated_image)
%         drawnow()
%         title(['Rotation angle: ' int2str(angulo)])
%         hold off
%         set(gcf,'units','normalized','outerposition',[0 0 1 1]);        
    end


end
subplot(1,1,1)

if ~exist('num_peaks')
    fprintf('Not enough peaks found. Returning.\n')
    ignore_folder = true;
    return
end

[Y,I] = sort(num_peaks, 2, 'descend');
indices_max_count_peaks = find(num_peaks == Y(1)); %num_peaks(num_peaks==Y(1));

if length(indices_max_count_peaks) > 1
    max_sum_image = max_sum_image(indices_max_count_peaks);
    [Yx, Ix] = max(max_sum_image);  
    I = indices_max_count_peaks(Ix);
end

rotationAngle = angulos(I(1));
    
datenum_ini = files_images(1).datenum;
x_start = datenum_ini - mod(datenum_ini, 1/48);
x_end = x_start + 1/48;


if processing_session.makeVideo
    video_path_output = 'D:\Users\an\experimento-usb-interferometro\videos\';
    outputVideo = VideoWriter(fullfile(video_path_output, videoId));
    outputVideo.FrameRate = 10;
    open(outputVideo);
end

for i=1:length(files_images)
    fila = fila +1;

    name_image = files_images(i).name;
    if strfind(name_image, '\')
        full_name_image = name_image;
    else
        full_name_image = strcat(path_images, name_image);
    end   
    
    if ~exist('lastI', 'var') || (mod((i - lastI),100)==0)
        elapsed = toc(tini)/60;
        total = (maxfiles(1)*elapsed/i);
        faltante = (total-elapsed);
        if ((total-elapsed) < 1)
            faltante = (total-elapsed)*60;
        end
        fprintf('%d/%d - %6.1f - total est.: %4.2f min, transcurridos: %4.2f min, faltante: %4.2f min \n', i, maxfiles(1), round(i/maxfiles(1)*10000)/100, total, elapsed, faltante);
        lastI = i;
    end    
    if (i==332)
            a=1;
    end
 

%     if ~isfield(table2struct(conf), 'minY')
%         minY = 1;
%     end
%     if ~isfield(table2struct(conf),'maxY')
%         maxY = size(imagen,1);        
%     end   

%     imagen = imagen(minY:maxY, :);
    
%     if isfield(table2struct(conf), 'rotationAngle')
%         rotationAngle = conf.rotationAngle;
%     else
%        if exist('rotationStop', 'var') && rotationStop 
%            angle = 0;
%            imshow(imrotate(imagen, angle))
%            while true
%                answer = input('input a rotation angle and press Enter (rotationAngle):');
%                  answer =[];
%                if isempty(answer)               
%                    break
%                end
%                angle = answer;
%                imshow(imrotate(imagen, angle))
%            end
%            rotationAngle = angle;
% %         else
%             
% %             angle=0;
% %             rotationAngle = angle;
%        end
%         
%        conf.rotationAngle = rotationAngle;
%        writetable(conf, fconf);          
%     end

    [imagen map]= imread(full_name_image);
    imagen = rgb2gray(imagen);
%     imagen = imadjust(imagen);
    imagen = imrotate(imagen, rotationAngle);     
    imagen = imfilter(imagen,fspecial('disk', filterDiskSize));
    
    perfil_intensidad = sum(imagen');
    [Y,I] = max(perfil_intensidad);
    if ~exist('max_intensity_row')
        max_intensity_row = I;
    end
    perfil = imagen(I,:);
    perfil = double(perfil);
       
    perfil = smooth(perfil, smooth_num_points);
    
    [peaks,locs] = findpeaks(perfil, 'MinPeakDistance', minpeakdistance);
    
    textPosition = 'bottom';
    if ~exist('figureCreated', 'var') || figureCreated==false
        
        xts(1) = x_timestamp(1);
        imshow(imread(full_name_image))
        axis on
        xlabel('Width of original image (px)')
        ylabel('Height of original image (px)')
        title('First image of session (original)')
        textPosition = 'bottom';
        usb2018_saveFigureToFile('_original_image', 'numFig', false, ...
            'useXts', false, 'textPosition', textPosition, 'timeRange', [x_start x_end])
        
        imshow(imagen)
        
        axis on
        hold on
        minsizeimagen = min(size(imagen));
        plot(-3/5*minsizeimagen*perfil/max(max(perfil))+minsizeimagen, 'color','r', 'linewidth',2)
        xlabel('Width of rotated image (px)')
        ylabel('Height of rotated image (px)')
        title('First image of session after rotation, B&W, adjust and smoothing')
        textPosition = 'bottom';
        usb2018_saveFigureToFile('_with-intensity_profiles', 'numFig', false, ...
            'useXts', false, 'textPosition', textPosition, 'timeRange', [x_start x_end])
        
        figureCreated = true;
    end
    
%     try

        
        if length(peaks) >= 3
            try
                perfiles(fila,:,:) = perfil;        
            catch
                perfiles(fila,:,:) = nan(1, size(perfiles(fila-1,:,:),2));
                p(fila,1:length(locs)) = nan(1,length(locs)); % locs;          
                continue
            end
            p(fila,1:length(locs)) = locs;        
%         elseif size(perfiles,2) ~= length(perfil)
%             perfiles(fila,:,:) = nan(1, size(perfiles(fila-1,:,:),2));
%             p(fila,1:length(locs)) = nan(1,length(locs)); % locs;          
%         else
%             perfiles(fila,:,:) = perfil;        
%             p(fila,1:length(locs)) = nan(1:length(locs)); % locs;          
%             continue
    %         perfiles(fila,:,:) = perfiles(fila-1,:,:);
    %         p(fila, :) = p(fila-1, :);                
    %         continue;
        end
        if processing_session.makeVideo
            if ~exist('maximized', 'var') || ~maximized
                figure
                hold on
                set(gcf,'units','normalized','outerposition',[0 0 1 1]);
                maximized=true;
                ax = gca;
                height_profile = ax.YLim(2);
                perfil_xlim = [0 size(imagen,2)]
%                 [rotation90_pks,rotation90_locs]=findpeaks(sin(orientacion/360*2*pi),'minpeakdistance',30, 'MinPeakHeight', 0.95);
%                 [rotation0_pks,rotation0_locs]=findpeaks(sin(orientacion/360*2*pi + pi/2),'minpeakdistance',30, 'MinPeakHeight', 0.95);
            end
            subplot(2,2,2)
               
            plot(x_timestamp',p, '.')
            title({'Position of Interference Maxima vs Time (raw) '},'FontSize', 16);
            
            ax = gca;
            draw_rotations(rotation0_locs, ax.YLim, ax)
            
            grid on
%             for b=1:size(p,2);
%                 line([1 size(p,1)],[p(1,1) p(1,end)]);
%             end
            config_plot
           
            subplot(2,2,4)
            plot(perfil)
            hold on
            plot(locs,peaks,'ro')
            xlim(perfil_xlim)
            hold off
            
            subplot(2,2,[1;3])
            
            imshow(imagen)
%             axis normal
            
            title({'Photo of interference pattern at timestamp'},'FontSize', 16);
            text(20, 55,[datestr(x_timestamp(i), 'yyyy-mm-dd HH:MM')], 'Color', 'red', 'FontSize',16)
            text(20, 145,['Rot. angle:' num2str(orientacion(i)) '°'], 'Color', 'red', 'FontSize',16)
            hold on
%             minsizeimagen = min(size(imagen));
%             plot(-3/5*minsizeimagen*perfil/max(max(perfil))+minsizeimagen, 'color','r', 'linewidth',2)
            plot(locs, max_intensity_row, 'ro')
%             legend('Interference maxima')
%             ax=gca;

            drawnow()
            hold off
            frame = getframe(gcf); 
            writeVideo(outputVideo,frame.cdata)        
        end        
%     catch
%         a=1;
%     end
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
%     if exist('animar') & animar == true
%         plot(perfil)
%         hold on
%         plot(locs,peaks,'o')    
%         hold off
%         drawnow;
%     end
end

if processing_session.makeVideo
    close(outputVideo)
    subplot(1,1,1)
    hold off
end

% if exist('punto_inicial')
%     p = p(initial_point:end, :);
%     x_timestamp = x_timestamp(initial_point:end);
% end

p_orig = p;
x_timestamp_orig = x_timestamp;

xts = x_timestamp';

save([wspath videoId], '-regexp', '^(?!ses)...')
