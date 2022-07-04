function [ adjusteddata ] = adjustdata( data )
    %ADJUSTDATA(data) tries to find continuous series from a scrambled data
    %tiempo es 1era dimension de data

    if isempty('data')
        data = p_complete;
    end
    
    clc
    nAvg = 1;
    start = 1;

    data = double(data(start:size(data,1), :));
%     bucket = nan(size(data,1),80);
    bucket = [];
    createdBuckets = 0;
    for tiempo = 1 : size(data, 1)
        if (mod(tiempo, 1000) == 0) 
            fprintf('n: %d \n', tiempo);
        end        
        for col=1:size(data,2)

            val = data(tiempo, col);
            if val==0
                continue
            end

%              fprintf('tiempo:%d col:%d; val: %d \n', tiempo, col, val);
%              bucket
%              data(1:7,1:15)
             
            ok = 0;
            bestBucket = nan;
            for backtime = 1:1
                for b = 1:createdBuckets                
                    % if ~isnan(bucket(n-r,b))
                    %    fprintf('%6.6f', abs(bucket(n-r,b)-val));
                    %end
                    tiempoAnterior = max(1, tiempo - backtime);
                    while ~isnan(bucket(tiempoAnterior,b)) && tiempoAnterior-1 > 0 && ~isnan(bucket(tiempoAnterior-1,b)) && bucket(tiempoAnterior,b) == 0
                        tiempoAnterior = tiempoAnterior -1;
%                         fprintf('backtime:%d\n', tiempoAnterior);
                    end
%                     fprintf('backtime:%d, tiempo:%d \n', tiempoAnterior, tiempo);
                    if ~isnan(bucket(tiempoAnterior,b))

                        valorBucketAnterior = bucket(tiempoAnterior, b);
                        if (abs(valorBucketAnterior - val) < 50)
                            %  fprintf('\tdiff:%g \n', (abs(bucket(n-r,b)-val)));

                            if isnan(bestBucket) || (abs(valorBucketAnterior  - val) < bucket(tiempoAnterior, bestBucket))
                                bestBucket = b;
                            end             
                        end
                    end
                end
                if ~isnan(bestBucket)
                    bucket(tiempo,bestBucket) = val;
                    ok = 1;
                    break
                end
            end
            
            if ok==1
                continue
            else
                createdBuckets = createdBuckets + 1;
                bucket(tiempo, createdBuckets) = val;
            end
            if createdBuckets > 5000
                muchosBuckets = createdBuckets
                adjusteddata = bucket;
                return
            end
        end
    end
    bucket(bucket==0) = NaN;
    adjusteddata = bucket;
end

