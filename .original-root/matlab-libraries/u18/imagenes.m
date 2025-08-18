for i=1:5
    full_name_image = strcat(path_images, files_images((i-1)*1000+1).name)
    [imagen map]= imread(full_name_image);
    figure
    image(imagen)
end