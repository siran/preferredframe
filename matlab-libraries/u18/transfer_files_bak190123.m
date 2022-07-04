function transfer_files(tobo_files, path_tobo, path_data)
    for i=1:length(tobo_files)
        if ~exist('session_name')
            base_session_name = datestr(tobo_files(i).datenum, 'YYmmdd');
            session_name = findNextSessionName(base_session_name, path_data);        
        end

        fname = tobo_files(i).name;
        tobo_datetakennum = tobo_files(i).datetakennum;
        src = [path_tobo fname];     
        if exist('dest')
            dest_old = dest;
        end
        dest = [path_data session_name '\' fname];
        
        if exist(dest, 'file')
            continue
        end
        
        if i > 1
            tobo_datetakennum_old = tobo_files(i-1).datetakennum;       
        else
            session_files = getSessionFiles(session_name, path_data)
            if length(session_files) == 0
                tobo_datetakennum_old = tobo_files(i).datetakennum;       
            else
                tobo_datetakennum_old = session_files(end).datetakennum;       
            end
        end
        
        tobo_datetakennum = tobo_files(i).datetakennum;
        if abs(tobo_datetakennum_old - tobo_datetakennum) > 1/24/60
            old_base_session_name = session_name(1:strfind(session_name, '_') - 1);
            new_base_session_name = datestr(tobo_files(i).datetakennum, 'YYmmdd');
            if strcmp(old_base_session_name, new_base_session_name)
                session_index = str2num(session_name(strfind(session_name, '_')+1:end)) + 1;    
                session_name = [old_base_session_name '_' num2str(session_index)];    
            else
                session_index = 1;
                session_name = [new_base_session_name '_' num2str(session_index)];    
            end
            mkdir(path_data, session_name)
        end    

        fname = tobo_files(i).name;
        dest = [path_data session_name '\' fname];
        if ~exist(dest, 'file')
%             copyfile(src, dest)
            movefile(src, dest)
        else
            fprintf('%s already exists in destination \n', fname)
        end

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
