% attemps to find the coefficients which render the differences between
% fringes, temperature, pressure and humidity
% that is to find the minimum discrete summation of the differences 
% sum over t : fringe(t) - k1*T(t) - k2*P(t) - k3*H(t)

clear differences Y I

if (exist('flatpointst') | exist('flatpointsh') )
%     i_temp_1 is the value of temperatura for the first point of flat
%     humidity ...
%     i_temp_1 = s_i_temp(flatpointsh(1).DataIndex);
%     i_temp_2 = s_i_temp(flatpointsh(2).DataIndex);
%     
%     i_hum_1 = s_i_hum(flatpointst(1).DataIndex);
%     i_hum_2 = s_i_hum(flatpointst(2).DataIndex);
%     
%     pt_1 = p(flatpointsh(1).DataIndex);
%     pt_2 = p(flatpointsh(2).DataIndex);
%     
%     ph_1 = p(flatpointst(1).DataIndex);
%     ph_2 = p(flatpointst(2).DataIndex);
    
    steps = 100;
    
%     mct = (pt_2 - pt_1)/(i_temp_2-i_temp_1) / 1.2;
%     Mct = (pt_2 - pt_1)/(i_temp_2-i_temp_1) * 1.2;
%     sct = (Mct-mct)/steps;

    mct = (335.9-146)/(38.6-38.9);
    Mct = (335.9-146)/(38.6-38.9);
    sct = 1;
    
%     mch = (ph_2 - ph_1)/(i_hum_2-i_hum_1) / 1.2;
%     Mch = (ph_2 - ph_1)/(i_hum_2-i_hum_1) * 1.2;
%     sch = (Mch-mch)/steps;

    mch = (154.6-123.8)/(27.9-27.73);
    Mch = (154.6-123.8)/(27.9-27.73);
    sch = 1;%(Mch-mch)/steps        
else
    fprintf(['Error: "flatpointst and/or flatpointsh data arrays not found" \n ' ...
        'Please run graficar_tph_con_ejes and extract two arrays of 2 datapoints ' ...
        'each called flatpoints and flatpointsh:\n first two points are flat temperature, next two points are flat humidity\n']);
    return;
end

meant = mean(s_i_temp);
meanp = mean(s_i_pressure);
meanh = mean(s_i_hum);

% we need to interpolate temp, pressure and hum to match with x_timestamp,
% we call these itemp, ipressure, ihum: i stand for interpolated
% tt is the time axis for temperature, p and hum
% tm=x2mdate(tt);
% xts = x_timestamp';

%interpolate to fringe measurements
% itemp = pchip(tm, temp, xts);
% ipressure = pchip(tm, pressure, xts);
% ihum = pchip(tm, hum, xts);

% c stands for 'coefficient', thus ct=temperature coefficient
% m or M stands for minumum or Maximum values to try
% s stand for stemp to make
row = 0;
index=0;
step = 0.5;

totalrows = (Mct-mct)/sct * (Mch-mch)/sch;

for ch = mch:sch:Mch
    for ct = mct:sct:Mct
%     for cp = mcp:scp:Mcp

            row = row+1;
            if (mod(row,200)==0)
                   fprintf('%d/%d \n', row, totalrows);
            end
            % w calculate the differences that we want to minimize
            % m stand for matrix, mc matrix of coefficients
%             mc(row) = [ct cp ch];
             mc(row,1) = ct;
             mc(row,2) = ch;
%             difference(row) = sum(p - ct*(itemp-meant) - cp*(ipressure-meanp) - ch*(ihum-meanh));
            difference = sum(abs(p - ct*(s_i_temp-meant) - ch*(s_i_hum-meanh)));
            plot(xts, p, xts, p - ct*(s_i_temp-meant) + ch*(s_i_hum-meanh), 'green');
            drawnow;
            if (~exist('differences') | difference <= min(differences))
                index = index+1;
                differences(index) = difference;
                mc(index,1) = ct;
                mc(index,2) = ch;
            end
        end            
%     end
end

    [Y, I] = min(differences);
mc(I);
% plot(xts, p - mc(I,1)*(s_i_temp-meant) - mc(I,2)*(s_i_hum-meanh))
lineasestelares

