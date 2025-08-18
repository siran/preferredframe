datas = nan(size(data));

for d=1:size(data,2)
    fprintf('col: %d \n', d);
    datas(:,d) = smooth(data(:,d), 50);
end
