function [ adjusteddata ] = adjustdata( data )
    %ADJUSTDATA(data) tries to find continuous series from a scrambled data

    clc
    nAvg = 1;
    start = 1;

    data = double(data(start:size(data,1), :));
    bucket = nan(size(data,1),80);
    createdBuckets = 0;
    for n = 1 : size(data, 1)
        if (mod(n, 1000) == 0) 
            fprintf('n: %d \n', n);
        end        
        for col=1:size(data,2)
%             fprintf('n:%d col:%d \n', n, col);
            val = data(n, col);
            if val==0
                continue
            end
            
            ok = 0;
            for r = 0:min(15, n-1)
                for b = 1:createdBuckets                
                    if  ~isnan(bucket(n-r,b)) && abs(bucket(n-r,b)-val)<20 
                        bucket(n,b) = val;
                        ok = 1;
                        break                    
                    end
                end
                if ok==1
                    break
                end
            end
            
            if ok==1
                continue
            else
                createdBuckets = createdBuckets + 1;
                bucket(n, createdBuckets) = val;
            end
        end
    end
%     bucket(bucket==0) = NaN;
    adjusteddata = bucket;
end

