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

stars = {'HIP54589', 'Sun', 'Moon'};
for starname_i = 1:length(stars)

height_star_data_path = 'D:\Users\an\experimento-usb-interferometro\height-star\';
star_name=stars{starname_i};
altitude_filename = [height_star_data_path 'heightstar-' star_name '-' ...
        datestr(date_start, 'YYYY') '-' datestr(date_start, 'mm') '.csv' ];  
    
loadfile = true;
% if exist('timeAltitude', 'var') && ~isempty(timeAltitude)
%     altitude_date_start = timeAltitude(1,1);
%     altitude_date_end   = timeAltitude(end,1);
%     if x_start >= altitude_date_start && x_end <= altitude_date_end
%         loadfile = false;
%     end
% end
        
if loadfile && exist(altitude_filename, 'file')
    fprintf(['Loading altitude/azimuth for star' star_name '\n'])
    % [numData,textData,rawData] = xlsread(altitude_filename, 'basic');

    rawData = readcell(altitude_filename);

    for r=1:size(rawData,1)
        t=r;
        timeAltitude(t,1,starname_i)=datenum(datetime(rawData{r,1},'InputFormat','yyyy-MM-dd''T''HH:mm:ss'))+1/24*4;
        timeAltitude(t,2,starname_i)=rawData{r,5}; % equatorial altitude
        timeAltitude(t,3,starname_i)=rawData{r,4}; % equatorial azimuth
        if size(rawData,2)>5 && ~strcmp(rawData{r,7}, 'undefined')
            timeAltitude(t,4,starname_i)=rawData{r,7}; % distance to Earth in km
        end
        stop=1;
    end
end
end
       

s=1;

