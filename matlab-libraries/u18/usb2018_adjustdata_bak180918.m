function [ adjusteddata ] = adjustdata( data )
    %ADJUSTDATA(data) tries to find continuous series from a scrambled data
    %tiempo es 1era dimension de data

%     global p_orig
%     
%     if isempty('data') || ~exist('data')
%         data = p_orig;
%     end
    
    clc
    nAvg = 1;
    start = 1;

%     data = double(data(start:size(data,1), :));
%     bucket = nan(size(data,1),80);
    bucket(1,1) = nan;
    createdBuckets = 1;
    for tiempo = 1 : size(data, 1)
%         if (mod(tiempo, 1) == 0) 
%             fprintf('n: %d \n', tiempo);
%         end        
        for col=1:size(data,2)

            val = data(tiempo, col);
            valanterior = data(tiempo, max(col-1, 1));
            if val==0
                continue
            end           
%             fprintf('n: %d val: %d ValAnterior: %d Diff: %d \n', tiempo, val, valanterior, 2);
                         
            ok = 0;
            bestBucket = nan;
%             if tiempo>4
%                 bucket(size(bucket,1)-3:size(bucket,1), :)
%                 a=1;
%             end
            for backtime = 1:1
                for b = 2:createdBuckets                
                    tiempoAnterior = max(1, tiempo - backtime);
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
                    if ~isnan(bucket(tiempoAnterior,b))
                        valorBucketAnterior = bucket(tiempoAnterior, b);
                        if (abs(valorBucketAnterior - val) < 58)
%                              fprintf('\tdiff:%g \n', valorBucketAnterior - val);

                            if isnan(bestBucket) || (abs(valorBucketAnterior  - val) < bucket(tiempoAnterior, bestBucket))
                                bestBucket = b;
                            end             
                        end
                    end
                end
            end
            if ~isnan(bestBucket)
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
                createdBuckets = createdBuckets + 1;
                bucket(tiempo, createdBuckets) = val;
            end
            if createdBuckets > 200
                muchosBuckets = createdBuckets
                adjusteddata = bucket;
                return
            end
        end
    end
    bucket(bucket==0) = NaN;
    if size(bucket,1) ~= size(data,1)
        a=1;
    end
    adjusteddata = bucket;
end

