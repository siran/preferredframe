% prepare packets

destination_dir = 'G:\My Drive\preferred-frame\usb-one-way\';



% copy to destination

source_package_directory = [pathToFigures package_name '\'];

figure_type = 'rotaciones-promediadas-normalizadas';
figure_path = [destination_dir figure_type '\'];
destination_package_directory = [figure_path figure_type '-' package_name];



mkdir(figure_path, [figure_type '-' package_name])
% copyfile( ...
%     'D:\Users\an\experimento-usb-interferometro\figures\20191001-20191019\*mean-group-r10s10-normalized-alt*.jpg', ...
%     'G:\My Drive\preferred-frame\usb-one-way\rotaciones-promediadas-normalizadas\rotaciones-promediadas-normalizadas-20191001-20191019')

copyfile( ...
    [source_package_directory '*mean-group-r10s10-normalized-alt*.jpg'], ...
    destination_package_directory)

a=1;