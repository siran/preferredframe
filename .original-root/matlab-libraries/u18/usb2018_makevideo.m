% make video from source images

warning('off', 'MATLAB:imagesci:tifftagsread:expectedTagDataFormat')
warning('off', 'images:initSize:adjustingMag')
warning('off', 'MATLAB:audiovideo:VideoWriter:noFramesWritten')

% path_images = 'C:\Users\an\Documents\megasync-preferredframe\180820\con-rotacion\';
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

imageNames = dir(fullfile(path_images,'*.jpg'));
imageNames = {imageNames.name}';

outputVideo = VideoWriter(fullfile(path_output, videoName));
outputVideo.FrameRate = 4;
open(outputVideo);

% [a, MSGID] = lastwarn()

for ii = 1:length(files_images)
    if (mod((ii),100)==0)
        fprintf('%d ', ii)
    end
    exifinfo = imfinfo(fullfile(path_images, imageNames{ii}));
    datestr = exifinfo.DateTime;
    orientacion = exifinfo.GPSInfo.GPSImgDirection;
    
    img = imread(fullfile(path_images, imageNames{ii}));
    imshow(img);
%     [a, MSGID] = lastwarn()
    text(25,length(img)-100,{datestr, strcat(num2str(orientacion, '%06.2f'), 'º'), ['frame ' num2str(ii) '/' num2str(length(files_images))]}, 'color', 'white', 'fontsize', 12,'backgroundColor','black', 'fontname', 'consolas')
    img2 = getframe(gca); 
    writeVideo(outputVideo,img2.cdata)
end

close(outputVideo)