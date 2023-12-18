% make video from source images

warning('off', 'MATLAB:imagesci:tifftagsread:expectedTagDataFormat')
warning('off', 'images:initSize:adjustingMag')
warning('off', 'MATLAB:audiovideo:VideoWriter:noFramesWritten')
warning('off', 'MATLAB:Axes:UnsupportedDataAspectRatio')

path_output = 'D:\Users\an\candlelight-experiment\videos';
% path_images = 'D:\Users\an\experimento-usb-interferometro\tobo-ordenado\2021-02-06\n210206_0930\';
% videoId = 'n210202_0500'

%     ,'D:\Users\an\experimento-usb-interferometro\tobo-ordenado\2021-03-27\n210327_0930' ...
%     ,'D:\Users\an\experimento-usb-interferometro\tobo-ordenado\2021-03-27\n210327_1000' ...
path_images = {...
    '' ...
%     ,'G:\My Drive\preferred-frame\usb-one-way\rotaciones-promediadas-normalizadas\rotaciones-promediadas-normalizadas-20191001-20191019' ...
    destination_package_directory
};

for i = 1:length(path_images)
    
    if isempty(path_images{i})
        continue
    end
    
    files_images = dir(strcat(path_images{i},'\*.jpg'));
    
    [path, filename, extention] = fileparts(path_images{i});
    
    % ordeno por fecha
%     for t=1:size(files_images)
%         files_images(t).name = files_images(t).name;
%     end
    [tmp ind]=sort({files_images.name});
    files_images = files_images(ind);

    outputVideo = VideoWriter(fullfile(path_output, filename));
    outputVideo.FrameRate = 4;
    open(outputVideo);

    for ii = 1:length(files_images)
        if (mod((ii),100)==0)
            fprintf('%d ', ii)
        end

        imageName = files_images(ii).name;  
        img = imread(fullfile(path_images{i}, imageName));
        imshow(img);

        img2 = getframe(gca); 
        try
            writeVideo(outputVideo,img2.cdata)
        catch
            continue
        end
    end

    close(outputVideo)
end