function [ adjusteddata ] = adjustdata( data )
    %ADJUSTDATA(data) tries to find continuous series from a scrambled data
    %tiempo es 1era dimension de data

%     global p_orig
%     
%     if isempty('data') || ~exist('data')
%         data = p_orig;
%     end
    
%     clc
    nAvg = 1;
    start = 1;

%     data = double(data(start:size(data,1), :));
%     bucket = nan(size(data,1),80);
%     bucket(1,1) = nan;
    createdBuckets = 1;
%     newbucket = nan(size(data,1), size(data,2)*10);
    left = 1;
    right = size(data,2);    
    bucket(1, :) = data(1, :);
%     data1 = size(data,1);
%     data2 = size(data,2);
    for tiempo = 2 : size(data, 1)
          shifted=false;
%         if (mod(tiempo, 1) == 0) 
%             fprintf('n: %d \n', tiempo);
%         end  
%         data(tiempo+1,1:9) - data(tiempo,1:9)

        data1 = data(tiempo-1, :);
        data2 = data(tiempo, :);
%         data2(isnan(data2)) = data1(isnan(data2));
%         data1(isnan(data1)) = data2(isnan(data1));
%         data2(isnan(data2)) = 0;
%         data1(isnan(data1)) = 0;
        [data1' data2']
        s1=data1';
        s2=data2';
        [acor,lag] = xcorr(s2,s1);
        [~,I] = max(abs(acor));
        lagDiff = lag(I)
        
        if abs(s1(1) - s2(1)) > 10
            stop=1;
        end

        if abs(lagDiff) > 0
%             if tiempo > 50
            fprintf('t: %03d, sum: %03d', tiempo, abs(nansum(data(tiempo+1,:) - data(tiempo,:))))
            fprintf('\n')            
            fprintf('%03d ', data1(:))
            fprintf('\n')
            fprintf('%03d ', data2(:))
            fprintf('\n')
            fprintf('%03d ', data1 - data2)
            fprintf('\n')
            fprintf('\n')
%             end
            
            sumRight = abs(nansum(data(tiempo-1,left:right-1) - data(tiempo,left+1:right)));
            sumLeft = abs(nansum(data(tiempo-1,left+1:right) - data(tiempo,left:right-1)));
            
            fprintf('right: %3d\n', sumRight)
            fprintf('left: %3d\n', sumLeft)
            
            if sumRight < sumLeft
                right = right - 1;
                fprintf('right -1 to: %d\n', right)
            elseif sumRight > sumLeft
                left = left + 1;
                fprintf('left +1 to: %d\n', left)
            else
                tiempo
            end          
            
%             if tiempo > 50
%             fprintf('t: %03d, sum: %03d', tiempo, abs(nansum(data(tiempo+1,:) - data(tiempo,:))))
%             fprintf('\n')            
%             fprintf('%03d ', data(tiempo-1, left:right))
%             fprintf('\n')
%             fprintf('%03d ', data(tiempo,left:right))
%             fprintf('\n')
%             fprintf('%03d ', data(tiempo, left:right) - data(tiempo-1,left:right))
%             fprintf('\n')
%             fprintf('\n')
%             end          
            
%             fprintf('right:\n')
%             fprintf('%03d ', data(tiempo,left:right-1))
%             fprintf('\n')
%             fprintf('%03d ', data(tiempo+1,left+1:right))
%             fprintf('\n')
%             fprintf('sum right: %03d', ...
%                 abs(nansum(data(tiempo,left:right-1) - data(tiempo+1,left+1:right))) ...
%             )
%             fprintf('\n')
% 
%             fprintf('left:\n')
%             fprintf('%03d ', data(tiempo,left+1:right))
%             fprintf('\n')
%             fprintf('%03d ', data(tiempo+1,left:right-1))
%             fprintf('\n')
%             fprintf('sum left: %03d', ...
%                abs(nansum(data(tiempo,left+1:right) - data(tiempo+1,left:right-1))) ... 
%             )        
%             fprintf('\n')
            shifted=true;
        end
        if right-left < 3
            stop=1;
        end
%         if mod(tiempo, 867) == 0
%             plot(bucket)
%             stop=1;
%         end
        row = [nan(1, left-1) data(tiempo,1:right-left+1) nan(1, size(data,2)-right)];
        bucket(tiempo, :) = row;      
        if shifted && tiempo > 867
            % tiempo > 57
            fprintf('t: %d\n', tiempo)
            fprintf('data\n', tiempo)
            data(tiempo-10:tiempo, 1:10)
            fprintf('bucket\n', tiempo)
            bucket(tiempo-10:tiempo, 1:10)
            data1 = data(tiempo-1, :);
            data2 = data(tiempo, :);
            data1(isnan(data1)) = 0;
            data2(isnan(data2)) = 0;
            [Y I] = min(conv(data1, data2, 'same'));
            fprintf('conv: %d\n', Y)
        end
        
        left = 1;
        right = size(data,2); 
        
    end
    adjusteddata = bucket;
end

