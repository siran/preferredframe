% colorMap = hot(40);
% 
% figure
% for c=1:length(colorMap)
%     line([0 10],[(c-1)*5 (c-1)*5], 'Color', colorMap(c,:))
% end
% return

% read datetime/alt from stellarium

% datetime('2018-09-01T12:12:12','InputFormat','yyyy-MM-dd''T''HH:mm:ss')

% [numData,textData,rawData] = xlsread('D:\Users\an\experimento-usb-interferometro\tiempo_vs_alt_hip54589_200201-200531.csv');

global timeAltitude

height_star_data_path = 'D:\Users\an\experimento-usb-interferometro\height-star\';
star_name='HIP54589';
altitude_filename = [height_star_data_path 'heightstar-' star_name '-' ...
        datestr(date_start, 'YYYY') '-' datestr(date_start, 'mm') '.csv' ];  
    
loadfile = true;
if exist('timeAltitude', 'var') && ~isempty(timeAltitude)
    altitude_date_start = timeAltitude(1,1);
    altitude_date_end   = timeAltitude(end,1);
    if x_start >= altitude_date_start && x_end <= altitude_date_end
        loadfile = false;
    end
end
        
if loadfile && exist(altitude_filename, 'file')
    fprintf(['Loading altitude/azimuth for star' star_name '\n'])
    [numData,textData,rawData] = xlsread(altitude_filename);

    for r=1:size(rawData)
        t=r;
        timeAltitude(t,1)=datenum(datetime(rawData{r,1},'InputFormat','yyyy-MM-dd''T''HH:mm:ss'))-1/24*4;
        timeAltitude(t,2)=rawData{r,5};
        timeAltitude(t,3)=rawData{r,4};
        stop=1;
    end
end
       

s=1;
