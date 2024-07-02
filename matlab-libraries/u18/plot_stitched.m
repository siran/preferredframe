

clc

figure 
hold on

bestline = 7;
p_complete = [];
xts_complete = [];
for psi = 1:length(p_struct)

    bestline = nan;

    x = p_struct(psi).xts;
    y = p_struct(psi).p_all;
    
    plot(x, y)

    % manual adjustments
    if psi == 1
        bestline = 7; %plot(x, y(:, best_line),'ro')
    elseif psi == 15
        bestline = 7;
    elseif psi == 16
        a=2;
    end

    if ~isnan(bestline)
        disp("psi " + psi + " manual adjustment")
        p_struct(psi).manual = true;
    end

    if isnan(bestline)
    
        % find best matching line
        window = 40;
        % previous_points = mean(p_struct(psi-1).p_all(end-window:end, bestline), 'omitnan');
    
        % y(isnan(y)) = -1;

        ym(y(1:window,:)==0) = nan;
        points = mean(y(1:window,:), "omitnan");
    
        difference = abs(points-previous_points);
        [ydiff, bestlines] = sort(difference);
            
        bestline = bestlines(1);
    end

    plot(x, y(:, bestline),'ro')

    xts_complete = cat(1, xts_complete, x);
    p_complete = cat(1, p_complete, y(:, bestline));
    
    
    previous_points = mean(p_struct(psi).p_all(end-window:end, bestline), 'omitnan');    
    p_struct(psi).bestline = bestline;
    

end