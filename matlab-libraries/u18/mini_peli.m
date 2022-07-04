clear f fs

for i=1:51
    ima = imread([path_images files_images(9130+i).name]);
    fprintf('%d %d %s\n', size(rgb2gray(ima),1), size(rgb2gray(ima),2), files_images(9148+i).date)
%     c = cat(3,rgb2gray(imread([path_images files_images(9148+i).name])),rgb2gray(imread([path_images files_images(9148+i+1).name])));
end