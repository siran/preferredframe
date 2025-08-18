% make video from source images

warning('off', 'MATLAB:imagesci:tifftagsread:expectedTagDataFormat')
warning('off', 'images:initSize:adjustingMag')
warning('off', 'MATLAB:audiovideo:VideoWriter:noFramesWritten')
warning('off', 'MATLAB:Axes:UnsupportedDataAspectRatio')


% path_images = 'C:\Users\an\Documents\megasync-preferredframe\figures\maxima-displacement-0404-0405\';
% path_output = 'D:\Users\an\experimento-usb-interferometro\videos\'
% videoId = '190404-190405-maxima-displacement'
if (~exist('files_images'))
    % leo archivos
    files_images = dir(strcat(path_images,'*.jpg'));

    % ordeno por fecha
    for t=1:size(files_images)
        full_name_image = [path_images files_images(t).name];
        info = imfinfo([path_images files_images(t).name]);
        date = info.DateTime;
        files_images(t).datenum = datenum(datetime(date,'InputFormat','yyyy:MM:dd H:m:s'));
    end
    [tmp ind]=sort([files_images.datenum]);
    files_images = files_images(ind);
end

imageNames = dir(fullfile(path_images,'*.jpg'));
imageNames = {imageNames.name}';

outputVideo = VideoWriter(fullfile(path_output, videoId));
outputVideo.FrameRate = 4;
open(outputVideo);

fconf = [path_images videoId '.csv'];
if exist(fconf, 'file')
    conf = readtable(fconf);   
    fields = fieldnames(conf);
    for f=1:length(fields)
        if ~strcmp(fields{f},'Properties')
            eval([fields{f} '=conf.(fields{f})'])
        end
    end
else
    conf = {};
end

if ~isfield(table2struct(conf), 'minY')
    minY = 1;
end
if ~isfield(table2struct(conf),'maxY')
    maxY = size(imagen,1);        
end   

% [a, MSGID] = lastwarn()

for ii = 1:length(files_images)
    if (mod((ii),100)==0)
        fprintf('%d ', ii)
    end
    imageName = files_images(ii).name;
    exifinfo = imfinfo(fullfile(path_images, imageName ));
    datestr_video = exifinfo.DateTime;
    orientacion_frame = exifinfo.GPSInfo.GPSImgDirection;
    
    img = imread(fullfile(path_images, imageName));
    
    img = rgb2gray(img);
    if strcmp(class(conf), 'table')
        if ~isfield(table2struct(conf), 'minY')
            minY = 1;
        end
        if ~isfield(table2struct(conf),'maxY')
            maxY = size(img,1);        
        end   
    else
        if ~isfield(conf, 'minY')
            minY = 1;
        end
        if ~isfield(conf,'maxY')
            maxY = size(img,1);        
        end   
    end    
%     img = img(minY:maxY, :);
    img = imadjust(img);
    img = imrotate(img, rotationAngle);     
    img = imfilter(img,fspecial('disk', filterDiskSize));    

    perfil = mean(img);
    perfil = double(perfil);
%     perfil=smooth(perfil);    
    [peaks,locs] = findpeaks(perfil, 'MinPeakDistance',50);      
      
    m = -1*round(size(img,1)/max(max(perfil))/2);
    b = round(size(img,1)/2);
    b = size(img,1);
    
    imshow(img);
    hold on    
    plot(m*perfil + b, 'color','r', 'linewidth',1)
    plot(locs, m*peaks + b, 'go')
    
    for L=1:length(locs)
        line([locs(L) locs(L)],[1 b/2], 'color', 'g')
    end
    hold off

    
    
%     [a, MSGID] = lastwarn()
    
%     text(25,size(img, round(1+cos(rotationAngle/180*pi)))-100, { ...
    text(25,size(img,1)-100, { ...    
        ['Date: ' datestr_video], ...
        ['Compass: ' num2str(orientacion_frame, '%06.2f'), 'º'], ...
        ['Photo #: ' num2str(ii) '/' num2str(length(files_images))], ...
        }, ...
        'color', 'white', 'fontsize', 12,'backgroundColor','black', 'fontname', 'consolas')
    img2 = getframe(gca); 
    writeVideo(outputVideo,img2.cdata)
end

close(outputVideo)