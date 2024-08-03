% extracts a fixed block of pixels from a series of pictures

% clc
warning('off', 'imageio:tifftagsread:expectedTagDataFormat')

% block coordinates
y1 = 600;
y2 = 1280;
x1 = 142;
x2 = 720;

pictures_base_folder = 'D:\Users\an\experimento-usb-interferometro\tobo-ordenado'
pictures = dir([pictures_base_folder '\2020-02-20\**\*.jpg']);
% workspace_folder = 'D:\Users\an\experimento-usb-interferometro\u18_workspaces';
% workspaces = dir([workspace_folder '\wn2002??_????-adjusted_orig.mat']);

num_pics = length(pictures);

% reducing to at most 4 hours of pictures 
num_pics = min(12*60*20,length(pictures));

fprintf('Number of pictures %d \n', num_pics)

worldline = nan(num_pics, 1);
timestamps = nan(num_pics, 1);
angles = nan(num_pics, 1);

% figure 
% hold on
tic;
for pic_i = 1:num_pics
    if mod(pic_i, 300) == 0 || pic_i == 1
        fprintf('i:%d elapsed: %1.0fs remaining: %1.1fs or %1.1fmin \n', ...
            pic_i, toc, num_pics/pic_i*toc-toc, num_pics/pic_i*toc/60-toc/60)
    end
    pic_struct = pictures(pic_i);

    pic_fullname = [pic_struct.folder '\' pic_struct.name];
    [pic, map]= imread(pic_fullname);
    pic = rgb2gray(pic);
    % pic = imadjust(pic);

    info = imfinfo(pic_fullname);
    date = info.DigitalCamera.DateTimeOriginal;    

    if size(pic,1) < size(pic,2)
        pic = pic';
    end    
    
    % figure
    % imshow(pic) 
    % block = pic(y1:y2, x1:x2);
    % hold on
    % line([x1 x2], [y1, y2])
    % figure
    % imshow(block)

    % blocks average intensity
    average_intensity = sum(sum(pic(y1:y2, x1:x2)))/prod(size(pic(y1:y2, x1:x2)));

    worldline(pic_i, :) = 255 - average_intensity;
    timestamps(pic_i, :) = datenum(date,'yyyy:mm:dd HH:MM:SS');
    if isfield(info.GPSInfo, 'GPSImgDirection')
        angles(pic_i) = info.GPSInfo.GPSImgDirection;
    end

end

worldline(worldline>235)=nan;

xlabel('Time');
set(gca,'XMinorTick','on')
datetick('x', 'dd/mm HH:MM','keeplimits')

plot(timestamps, worldline)