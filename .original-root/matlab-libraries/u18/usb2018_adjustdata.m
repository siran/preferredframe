function [ adjusteddata ] = adjustdata( data, varargin )
    %ADJUSTDATA(data) tries to find continuous series from a scrambled data
    %tiempo es 1era dimension de data
    
    format bank

    % default values
    backInTime = 10;
    maxHeightDifference = 45;
    ratio_fringe_separation = .75;

    nVarargs = length(varargin);
    for k = 1:2:nVarargs
        if strcmp(varargin{k}, 'backInTime')
            backInTime = varargin{k+1};
        elseif strcmp(varargin{k}, 'maxHeightDifference')
            maxHeightDifference =  varargin{k+1};
        elseif strcmp(varargin{k}, 'ratio_fringe_separation')
            ratio_fringe_separation =  varargin{k+1};
        end
    end

    bucket = nan(size(data));
    % the initial bucket values is the average of the first 50 point
    bucket(1, :) = (mean(data(1:50, :), 'omitnan'));
    bucket(2, :) = (mean(data(1:50, :), 'omitnan'));
    
    %% code to draw horizontal line per every fringe
    %plot(data, '.')
    %hold on
    %for b=1:length(bucket);line([1 length(data)],[bucket(1,b) bucket(1,b)]);end
    
    % number of bucket created
    createdBuckets = 2; %length(bucket);
    
    % the maximum space between fringes is the mean of the cleaned
    % (hampeled) number of pixels between fringes 
    avgFringeSeparation = mean(hampel(diff(bucket(1,:))), 'omitnan');
    maxHeightDifference = ratio_fringe_separation*mean(hampel(diff(bucket(1,:))), 'omitnan');
    
    % these are the number of time steps we average to determine the best
    % bucket
    stepsBack = 40;
    
    nAvg = 1;
    start = 1;
    global xts
   
    tini=tic;
    tend = length(data);
    for tiempo = 2 : tend
        if (mod(tiempo,100)==0)
            elapsed = toc(tini)/60;
            total = tend*elapsed/tiempo;
            faltante = (total-elapsed);
            if ((total-elapsed) < 1)
                faltante = (total-elapsed)*60;
            end
            fprintf('%d/%d - %6.1f - total est.: %4.2f min, transcurridos: %4.2f min, faltante: %4.2f min \n', tiempo, tend, round(tiempo/tend,2), total, elapsed, faltante);
        end  

        % avgStepsBack has to be greater than 1
        % then we average last avgStepsBack        
        avgStepsBack = max(1, tiempo - stepsBack);

        
        for col=1:size(data,2)
            if tiempo > 2 && size(bucket,1) >= tiempo-1
                bucket(bucket==0) = nan;
                % avgBackBucket = mean(bucket(avgStepsBack:tiempo-1, :), 'omitnan');
               
                avgBackBucket2 = hampel(movmean(bucket(avgStepsBack:tiempo-1, :), [2 0], 'omitnan'));
                avgBackBucket = avgBackBucket2(end, :);
%                 como = 1;
            else
                try
                    avgBackBucket = bucket(avgStepsBack:tiempo-1, :);
                catch
                    force_break = true
                    break
                end
%                 como = 2;
            end            
            val = data(tiempo, col);
            if tiempo == 149 && val == 456
                stop=1;
            end            
            if val==0 || isnan(val)
                continue
            end               
%             if tiempo == 41
%                 stop=1;
%             end
            ok = 0;
            bestBucket = nan;
%             fprintf('\n')
% 

%             %%%%%%%%%%%%%%
%             %%%% Animate adjust lines
%             fprintf('val: %0.0f, max: %0.0f, min: %0.0f\n', val, nan, nan)
%             fprintf('%0.0f %0.0f %0.0f %0.0f %0.0f %0.0f %0.0f %0.0f \n', bucket(:,1:8)')
%             fprintf('\n')
%             plot(bucket, 'o-')
%             xlim([0, size(bucket,1)])
%             hold on
%             plot(data, '.')
%             plot(tiempo, val,'X')
%             hold off
%             drawnow()
%             %%%%%%%%%%%%%%%%%%%%%%%
            
            for b = 1:createdBuckets       
                if isnan(val)
%                     bestBucket = 1;
%                     ok=1;
                    break
                end
                if b == 5
                    stop=1;
                end
%                 % avgStepsBack has to be greater than 1
%                 % then we average last avgStepsBack
%                 avgStepsBack = max(1, tiempo - stepsBack);
                valorBucketAnterior = avgBackBucket(b);

                if val < valorBucketAnterior + maxHeightDifference ...
                        && val > valorBucketAnterior - maxHeightDifference 
%                 if (abs(valorBucketAnterior - val) < maxHeightDifference)
%                     if isnan(bestBucket) || (abs(valorBucketAnterior  - val) < abs(bucket(tiempo-1, bestBucket) - val))
                        if isnan(bestBucket) || abs(avgBackBucket(b)-val) < abs(avgBackBucket(bestBucket)-val)
                            bestBucket = b;
                        end
%                     end             
                end
            end
%             if isnan(val)
%                 continue
%             end
            if ~isnan(bestBucket)
                bucket(tiempo,bestBucket) = val;
            else
%                 s=1
%                 if    (     val > (min(nonzeros(bucket(end-1,:))) - avgFringeSeparation) ...
%                        )    ...
%                          && ...
%                        (    val < (max(nonzeros(bucket(end-1,:))) + avgFringeSeparation) ...
%                        )
                    createdBuckets = createdBuckets + 1;
                    bucket(tiempo, createdBuckets) = val;
%                 if createdBuckets < 40
% 
%                 else
%                     bucket(tiempo, 1) = nan;
%                 end
%                 end
            end
            if createdBuckets > 600
                muchosBuckets = createdBuckets
                adjusteddata = bucket;
                return
            end
        end
        if exist('force_break','var') && force_break
            break
        end
%         if mod(tiempo, 10000) == 0
%             p_adjusted = bucket;
%             fprintf('tiempo: %d, val: %02d, buckets: %d', tiempo, val, size(bucket,2))
%             fprintf('\n')
%             fprintf('%02d ', data(tiempo-1, 1:10))
%             fprintf('\n')
%             fprintf('%02d ', data(tiempo, 1:10))
%             fprintf('\n')     
%             plot(xts(1:size(p_adjusted,1)), p_adjusted, '.')
%             set(gca,'XMinorTick','on')
%             grid on
%             datetick('x', 'HH:MM')
%             stop=1;
%         end        
    end
    bucket(bucket==0) = NaN;
    if size(bucket,1) ~= size(data,1)
        a=1;
    end
    adjusteddata = bucket;
%     figure
%     plot(adjusteddata,'.')
%     figure
%     plot(data,'.')
end

