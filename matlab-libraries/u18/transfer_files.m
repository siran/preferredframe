function transfer_files(tobo_files, path_tobo, path_data)
    for i=1:length(tobo_files)
        t1 = datetime(datestr(tobo_files(i).datetakennum));
        t1.Minute = 30 * floor(t1.Minute/30);
        try
            session_name = strcat('n', datestr(t1,'yymmdd_HHMM'));
        catch
            continue
        end
        
        fname = tobo_files(i).name;
        src = [path_tobo fname];
        dest = [path_data session_name '\' fname];
        
        if ~exist([path_data session_name], 'file')
            mkdir(path_data, session_name)
        end 
%         if ~exist(dest, 'file')
            copyfile(src, dest)
            delete(src)
%             movefile(src, dest)
%         else
%             fprintf('%s already exists in destination \n', fname)
%         end

        if mod(i, 500) == 0
            fprintf('%d/%d ', i, length(tobo_files))
        end

    end
end

function session_name = findNextSessionName(base_session_name, path_data)
    session = dir(strcat(path_data, base_session_name, '*'));
    if isempty(session)
        session_index = 1;
        session_name = [base_session_name '_' num2str(session_index)];
        mkdir(path_data, session_name)
    else
        session_name = session(end).name;
    end
end

function session_files = getSessionFiles(session_name, path_data)
    % check and order files in session dir
    session_files = dir(strcat(path_data, session_name, '\*.jpg'));
    for s=1:length(session_files)
        if mod(s, 100) == 0
            fprintf('%d/%d ', s, length(session_files))
        end    
        info = imfinfo([path_data session_name '\' session_files(s).name]);
    %     indexcolon = strfind(info.DateTime(1:11), ':');
        info.DateTime([5 8])='-';
        session_files(s).datetaken = info.DateTime;
        session_files(s).datetakennum = datenum(info.DateTime);
    end        
    photos = [session_files(:).datenum];
    [tmp ind]=sort(photos);
    session_files = session_files(ind);
end
