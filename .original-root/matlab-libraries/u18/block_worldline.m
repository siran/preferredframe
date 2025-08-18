% extracts a fixed block of pixels from a series of pictures


ti = 21;
tf = 28;
for tday=ti:tf
    
session_date = ['2020-02-' int2str(tday)];
fprintf('tday: %d/%d, %s', tday, tf, session_date)


% clc
clearvars a* -except session_date tday tf
warning('off', 'imageio:tifftagsread:expectedTagDataFormat')

% rotation angle of pic to align horizontally
rotation_angle = -12;

% block coordinates (after rotation)
y1 = 1092;
y2 = 1111;
x1 = 360;
x2 = 685;



block_size = (x2-x1) * (y2-y1);
fprintf('block_size: %d\n', block_size)


% data_timelimit_h = 1;

pictures_base_folder = 'D:\Users\an\experimento-usb-interferometro\tobo-ordenado'
pictures = dir([pictures_base_folder '\' session_date '\**\*.jpg']);
% workspace_folder = 'D:\Users\an\experimento-usb-interferometro\u18_workspaces';
% workspaces = dir([workspace_folder '\wn2002??_????-adjusted_orig.mat']);

num_pics = length(pictures);

% reducing to at most data_timelimit_h hours of pictures 
% data_timelimit_h = 1;
% num_pics = min(data_timelimit_h*60*20, num_pics);

fprintf('Number of pictures %d \n', num_pics)

worldline = nan(num_pics, 1);
timestamps = nan(num_pics, 1);
angles = nan(num_pics, 1);

% figure 
% hold on
tic;
h = figure;
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
   
    % rotate image to make it easy to extract information
    pic = imrotate(pic, rotation_angle);

    info = imfinfo(pic_fullname);
    date = info.DigitalCamera.DateTimeOriginal;    

    if size(pic,1) < size(pic,2)
        pic = pic';
    end    
    
    % show picture
    % imshow(pic) 
    % draw coordinates of block on top of picture
    % hold on
    % line([x1 x2], [y1, y2])    

    % select portion of picture
    block = pic(y1:y2, x1:x2);

    % for debugging, adjust intensity
    if pic_i == 1        
        % adjustment 
        intensity_adjustment = 4;
    end    
    block = block.*intensity_adjustment;

    % show block (adds like 20min to process, good to debug)
    % imshow(block);
    
    % calculates value based on block
    block_val = sum(sum(block));

    % build wordline of block: calculated value, angle, timestamp
    worldline(pic_i, :) = block_val;
    timestamps(pic_i, :) = datenum(date,'yyyy:mm:dd HH:MM:SS');
    if isfield(info.GPSInfo, 'GPSImgDirection')
        angles(pic_i) = info.GPSInfo.GPSImgDirection;
    end

end

o = struct();
o.timestamp = timestamps;
o.timestamp_str = datestr(timestamps);
o.angles = angles;
o.worldline = worldline;

o.worldline(o.worldline < 1e5) = nan;
T = struct2table(o);
writetable(T,['worldline-' session_date '.csv']);
end

% plot(o.timestamp, o.worldline)
% set(gca,'XMinorTick','on')
% datetick('x', 'dd/mm HH:MM','keeplimits')

% xlabel('Time');
% legend('Intensity of fixed region of picture')
% title('Intensity of fixed region of pictures vs time')

