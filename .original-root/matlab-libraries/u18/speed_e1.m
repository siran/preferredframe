% extracts a fixed block of pixels from a series of pictures


format long

pictures_base_folder = 'D:\Users\an\experimento-usb-interferometro\electricity-speed\data\attempt2';
pictures = dir([pictures_base_folder '\*.jpg']);

% block coordinates (after rotation)
y1 = 417;
y2 = 417;
x1 = 71;
x2 = 937;

num_pics = length(pictures);

fprintf('Number of pictures %d \n', num_pics)

worldline = nan(num_pics, 20);
timestamps = nan(num_pics, 1);

figure 
hold on
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
    % pic = imrotate(pic, rotation_angle);

    info = imfinfo(pic_fullname);
    date = info.DigitalCamera.DateTimeOriginal;    

    if size(pic,1) > size(pic,2)
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
    % if pic_i == 1        
    %     % adjustment 
    %     intensity_adjustment = 4;
    % end    
    % block = block.*intensity_adjustment;

    % show block (adds like 20min to process, good to debug)
    % imshow(block);
    
    % calculates value based on block
    [PKS,LOCS] = findpeaks(double(block), 'MinPeakHeight', 200);
    % block_val = sum(sum(block));

    % build wordline of block: calculated value, angle, timestamp
    try
        worldline(pic_i, :) = [LOCS'; zeros(20 - numel(LOCS), 1)]';
    catch ME
        disp('error')
        disp(ME)
    end
    

    timestamps(pic_i, :) = datenum(date,'yyyy:mm:dd HH:MM:SS');
    if isfield(info.GPSInfo, 'GPSImgDirection')
        angles(pic_i) = info.GPSInfo.GPSImgDirection;
    end

end

o = struct();
o.timestamp = timestamps;
o.timestamp_str = datestr(timestamps);
% o.angles = angles;
o.worldline = worldline;

% T = struct2table(o);
% writetable(T,['worldline-' session_date '.csv']);
% end

wlrs = reshape(o.worldline', [], 1);
wlrs(wlrs<650) = nan;
wlrs(wlrs>800) = nan;

% plot(o.timestamp, o.worldline)
% set(gca,'XMinorTick','on')
% datetick('x', 'dd/mm HH:MM','keeplimits')

plot(wlrs,'.')

title('speed of electricy')
xlabel('almost 24h')
ylabel('nanoseconds delay between two cables')
ylabel('delay between two cables (nanoseconds)')

