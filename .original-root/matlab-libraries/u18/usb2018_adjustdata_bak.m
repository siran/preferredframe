function [ adjusteddata ] = adjustdata( data, varargin )
    %ADJUSTDATA(data) tries to find continuous series from a scrambled data
    %tiempo es 1era dimension de data

%     global p_orig
%     
%     if isempty('data') || ~exist('data')
%         data = p_orig;
%     end

    % default values
    backInTime = 30;
    maxHeightDifference = 45;

    nVarargs = length(varargin);
    for k = 1:2:nVarargs
        if strcmp(varargin{k}, 'backInTime')
            backInTime = varargin{k+1};
        elseif strcmp(varargin{k}, 'maxHeightDifference')
            maxHeightDifference =  varargin{k+1};
        end
    end
    backInTime = 30;
    maxHeightDifference = 15;    
    
    nAvg = 1;
    start = 1;
    global xts

%     data = double(data(start:size(data,1), :));
%     bucket = nan(size(data,1),80);
%     bucket(1,1) = nan;
    bucket = [];
    createdBuckets = 0;
    for tiempo = 1 : size(data, 1)
        if tiempo == 1
            bucket(tiempo, :) = data(tiempo, :);
            continue
        end
        if tiempo == 73
            stop=1
        end
%         if (mod(tiempo, 1) == 0) 
%             fprintf('n: %d \n', tiempo);
%         end        
        for col=1:size(data,2)

            val = data(tiempo, col);
            if val==0 || isnan(val)
                continue
            end               

%             valanterior = data(tiempo, max(col-1, 1));
        
%             fprintf('n: %d val: %d ValAnterior: %d Diff: %d \n', tiempo, val, valanterior, 2);
                         
            ok = 0;
            bestBucket = nan;
%             if tiempo>4
%                 bucket(size(bucket,1)-3:size(bucket,1), :)
%                 a=1;
%             end
            for backtime = 1:backInTime
                for b = 1:createdBuckets       
                    bucketHeight = size(bucket, 1);
                    tiempoAnterior = max(1, bucketHeight - backtime);
%                     while ~isnan(bucket(tiempoAnterior,b)) && tiempoAnterior-1 > 0 && ~isnan(bucket(tiempoAnterior-1,b)) && bucket(tiempoAnterior,b) == 0
%                         tiempoAnterior = tiempoAnterior -1;
% %                         fprintf('backtime:%d\n', tiempoAnterior);
%                     end
%                     fprintf('backtime:%d, tiempo:%d \n', tiempoAnterior, tiempo);
%                     if isnan(bucket(tiempoAnterior,b)) && isnan(val)
%                         bestBucket = b;
%                         break
%                     end
                    if isnan(val)
                        bestbucket = 1;
                        ok=1;
                        break
                    end
                    if isempty(bucket)
                        bucket(1,1) = val;
                        continue
                    end
                     if ~isnan(bucket(tiempoAnterior,b))
                        valorBucketAnterior = bucket(tiempoAnterior, b);
                        if (abs(valorBucketAnterior - val) < maxHeightDifference)
%                              fprintf('\tdiff:%g \n', valorBucketAnterior - val);

                            if isnan(bestBucket) || (abs(valorBucketAnterior  - val) < abs(bucket(tiempoAnterior, bestBucket) - val))
                                bestBucket = b;
                            end             
                        end
                    end
                end
            end
            if ~isnan(bestBucket) && ~isnan(val)
                bucket(tiempo,bestBucket) = val;
                ok = 1;
%                 break
            end            
            
%             if (isnan(val) || val==0 || ok==0) && tiempo == size(data, 1)
%                 if val==0
%                     val=nan
%                 end
%                 bucket(tiempo, createdBuckets) = val;
%                 a=1;
%             end
            if ok==0
                if createdBuckets < 40
                    createdBuckets = createdBuckets + 1;
                    bucket(tiempo, createdBuckets) = val;
                else
                    bucket(tiempo, 1) = nan;
                end
            end
%             fprintf('%02d ', bucket(tiempo,:))
%             fprintf('\n')            
            if createdBuckets > 600
                muchosBuckets = createdBuckets
                adjusteddata = bucket;
                return
            end
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
end

