% adhoc image processing for Prof Greaves

wdir = 'D:\Users\an\experimento-usb-interferometro\p10-processing\';

fname = [wdir 'p10-anomaly-cropped2.jpg'];

imagen = imread(fname);
imagenbw = rgb2gray(imagen);

outfile_fig  = [wdir 'p10-anomaly-matrix-cropped.jpg'];
outfile_csv  = [wdir 'p10-anomaly-matrix-cropped.csv'];
saveas(gcf, outfile_fig);
csvwrite(outfile_csv, imagenbw)

t = 1;
% for t = 1:2:15
    T = t;
    imagenf = imagenbw;
    imagenf(imagenbw < T) = 1;
    imagenf(imagenbw > T) = 0;
    
    imshow(imagenf)
    
    imagenf = imregionalmax(imagenf);
    imshow(imagenf)
    
    outfile_fig  = [wdir 'p10-anomaly-matrix-cropped-' int2str(T) '.jpg'];
    outfile_fig_encontrados  = [wdir 'p10-anomaly-matrix-cropped-encontrados' int2str(T) '.jpg'];
    outfile_csv  = [wdir 'p10-anomaly-matrix-cropped-' int2str(T) '.csv'];
    outfile_csv_encontrados  = [wdir 'p10-anomaly-matrix-cropped-encontrados' int2str(T) '.csv'];
    
    saveas(gcf, outfile_fig);
    csvwrite(outfile_csv, imagenf)
    
    [rows,cols] = find(imagenf);
    plot(cols, rows, 'x')
    title('Puntos encontrados')
    saveas(gcf, outfile_fig_encontrados);
    csvwrite(outfile_csv_encontrados, [cols rows])

% end

 
