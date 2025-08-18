% moves pictures from 'tobo' to versiones session folder
% more than 3 min between pictures creates a new session
warning('off', 'MATLAB:imagesci:tifftagsread:expectedTagDataFormat')

clear fname session_datetakennum session

% path_tobo = 'C:\Users\an\Documents\megasync-preferredframe\tobo\';
% path_tobo = 'D:\Users\an\experimento-usb-interferometro\megasync-data-auto-proc\';
path_tobo = 'D:\Users\an\experimento-usb-interferometro\data-by-day\2020-02-12\'
% path_tobo = 'D:\Users\an\__preferredframe-googledrive-sync\tobo\';
% sessions_folder = 'D:\Users\an\experimento-usb-interferometro\megasync-data-auto-proc\';
% sessions_folder = 'D:\Users\an\experimento-usb-interferometro\auto-proc\';
sessions_folder = 'D:\Users\an\experimento-usb-interferometro\auto-proc\';

numvalid = 0;
% leo archivos
if ~exist('tobo_files')
    tobo_files = dir(strcat(path_tobo,'*.jpg'));

    % ordeno por fecha
    % for t=1:size(tobo_files)
    %     tobo_files(t).datenum = mat2str(datenum(tobo_files(t).date));
    % end
    invalid_file_count = 0
    for i=1:length(tobo_files)
       try
           
            if mod(i, 100) == 0
                fprintf('%d/%d ', i, length(tobo_files))
            end    
            fname = [path_tobo tobo_files(i).name];
            info = imfinfo(fname);
        %     indexcolon = strfind(info.DateTime(1:11), ':');
            info.DateTime([5 8])='-';
            tobo_files(i).datetaken = info.DateTime;
            tobo_files(i).datetakennum = datenum(info.DateTime);
            numvalid = numvalid+1;
            final(i) = tobo_files(numvalid);
       catch
           invalid_file_count = invalid_file_count+1;
           delete(fname)
           continue
       end
    end
    fprintf('invalid file count: %d\n', invalid_file_count)
    dates=[final(:).datetakennum];
    [tmp ind]=sort(dates);
    final = final(ind);
end

transfer_files(final, path_tobo, sessions_folder)



