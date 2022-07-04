% scratch

l = length(session_ids);

unique_session_ids = {};

for i=1:length(session_ids)
    found = false;
    underscore_index = strfind(session_ids{i}, '_');
    day_name_session = session_ids{i}(1:underscore_index-1);
    for i2=1:length(unique_session_ids)
        if strcmp(day_name_session, unique_session_ids{i2})
            found = true;
            break
        end
    end
    if ~found
        unique_session_ids{end+1} = day_name_session;
    end
end
f=1;

