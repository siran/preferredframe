% general analysis of data directory

% onlySession = '2020-02-29_2020-03-01';
% clear onlySession

clear p x_timestamp xts ps peaks locs p_orig x_timestamp_orig perfiles ...
    lineaPreferida puntosSuavizadoPreferido tt azimuth rotationStop pathToFigures videoId 

% global path_images

% warning('off', 'MATLAB:imagesci:tifftagsread:expectedTagDataFormat')
% warning('off', 'images:initSize:adjustingMag')
% warning('off', 'MATLAB:audiovideo:VideoWriter:noFramesWritten')
warning('off', 'imageio:tifftagsread:expectedTagDataFormat')
animar = false;

base_output_path = 'D:\Users\an\experimento-usb-interferometro';
session_days_path = [base_output_path '\tobo-ordenado\'];

session_days = dir(session_days_path);
% ordeno por fecha
[tmp, ind]=sort({session_days.name});
session_days = session_days(ind);

for d=1:length(session_days)

    day = session_days(d).name;
    if strcmp(day, '.') || strcmp(day, '..') || strcmp(day, 'desktop.ini')
        continue
    end
    if exist('onlySession', 'var') 
        if ~strcmp(day, onlySession)
            continue
        end
    else

        if datenum(day) < floor(datenum(date_start)) || (exist('onlySession', 'var') && strcmp(day, onlySession))
            continue
        end
        if datenum(day) > floor(datenum(date_end))
            break
        end   

        if isfield(processing_session, 'ignore_datetime') && ...
           ~ isempty(find(ismember(...
                processing_session.ignore_datetime, ...
                session_days(d).name), 1))
            fprintf('Ignorando sesion %s\n', datestr(session_datenum, 'yyyy-mm-dd HH:MM'))
            continue
        end  
        if isfield(processing_session, 'ignore_date') && ...
           ~ isempty(find(ismember(...
                processing_session.ignore_date, ...
                session_days(d).name), 1)) 
%             && ...
%                 datestr(session_datenum, 'yyyy-mm-dd HH:MM') == processing_session.ignore_date
            fprintf('Ignorando dia %s\n', datestr(session_datenum, 'yyyy-mm-dd'))
            continue
        end          
    end



    path_sessions = [session_days_path  day '\'];
    sessionsx = dir(path_sessions);

    % ordeno sesiones por fecha
    [tmp, ind]=sort({sessionsx.name});
    sessionsx = sessionsx(ind);
%     day_session = true;

    for s=1:length(sessionsx)
        session = sessionsx(s).name;
   
        if  ~sessionsx(s).isdir  || ...
            strcmp(session, '.') || ...
            strcmp(session, '..') || ...
            strcmp(session, 'desktop.ini') || ...
            strcmp(session, 'ignored_images') || ...
            strcmp(session(end-3:end), '.csv')
            continue
        end
        
        session_datenum = datenum(session(end-10:end), 'yymmdd_HHMM');
        date_start_datenum = datenum(processing_session.date_start);
        if ~isempty(date_start)
            date_start_datenum = datenum(date_start);
        end
        date_end_datenum = datenum(processing_session.date_end);
        
        if session_datenum <  date_start_datenum || ...
            session_datenum > date_end_datenum || ...
            ~isdir([path_sessions session])
            continue
        end
                             
        if isfield(processing_session, 'ignore_datetime') && ...
           ~ isempty(find(ismember(...
                processing_session.ignore_datetime, ...
                datestr(session_datenum, 'yyyy-mm-dd HH:MM')), 1))
            fprintf('Ignorando sesion %s\n', datestr(session_datenum, 'yyyy-mm-dd HH:MM'))
            continue
        end
        if isfield(processing_session, 'ignore_folder') && ...
           ~ isempty(find(ismember(...
                processing_session.ignore_folder, ...
                session), 1))
            fprintf('Ignorando sesion %s\n', datestr(session_datenum, 'yyyy-mm-dd HH:MM'))
            continue
        end        
        fprintf('Procesando %s\n', datestr(session_datenum, 'yyyy-mm-dd HH:MM'))
        
        if strcmp(session, '.day_session') || processing_session.day_session
            day_session = true;
        end
     
        close all

        clear saveFigureToFile
        clear functions
        clearvars -except sessionsx s onlySessivideoon afterSession timeAltitude ...
            path_sessions path_sessions_not_used ...
            session day session_days day_session files_images day ...
            date_start date_end package_name usb_sessions process_sessions processing_session ...
            session_datenum ...
            sindex uindex y_scale ...
            base_output_path session_days_path

        global pathToFigures
        global saveFile
        global frameToTime
        global xts
        global p_orig
        global videoId
%         global timeAltitude


        if exist('onlySession', 'var')
            if ~strcmp(onlySession, session)
                continue
            end
        end
        if exist('afterSession', 'var')
            if ~exist('forcedContinue', 'var')
                forcedContinue = true;
            end
            if strcmp(afterSession, session)
                forcedContinue = false;
            elseif ~forcedContinue
                forcedContinue = true;
            end
            if forced_continue
                continue
            end        
        end  

        
        path_images = [path_sessions session '\'];    
        
        % TODO: if it isfiles a "day session" the idea is to load all pics, from
        % all folders of the date in the array; this used to work in the
        % past
        day_session = processing_session.day_session;
        if day_session
            session = day;
            videoId = ['wday' '-' datestr(datenum(date_start), 'yyyymmdd') ...
                              '-' datestr(datenum(date_end), 'yyyymmdd') ...
                              '-' session];
            wsname = [base_output_path '\u18_workspaces\' videoId '.mat'];
            if exist(wsname, 'file')
                load(wsname, '-regexp', '^(?!ses|tim|conf|videoId|y_scale|package_name|lineaPreferida|pathToFigures)...')
                clear lineaPreferida
            end
            if ~exist('files', 'var')
                path_images = path_sessions;
                sessions_in_folder = dir(path_sessions);
                clear files_images
                for folder_i = 1:length(sessions_in_folder)
                    session_in_folder = sessions_in_folder(folder_i).name;
                    folder_name = sessions_in_folder(folder_i).folder;
                    if strcmp(session_in_folder(1), '.') || ...
                            ~isdir(folder_name) || ...
                            strcmp(session_in_folder, 'ignored_images')
                        continue
                    end
                    
                    % leo archivos
                    path_session_folder = [folder_name '\' session_in_folder '\'];
                    if exist([path_session_folder 'skip'], 'file') || exist([path_session_folder '.skip'], 'file')
                        continue
                    end                

                    path_session_folder_images = [path_session_folder '*.jpg'];
                    pictures = dir(path_session_folder_images);

                    maxfiles = size(pictures, 1);
                    if maxfiles < 100
                        fprintf('Muy pocos archivos: %d, videoid: %s\n', maxfiles, path_session_folder_images)
                        continue
                    end 
                    %  aqui
                    info = imfinfo([path_session_folder pictures(1).name]);
                    date = info.DigitalCamera.DateTimeOriginal;
                    picture_datestr = datetime(date,'InputFormat','yyyy:MM:dd H:m:s');
                    
                    picture_limit_exceeded = false;
                    if datenum(picture_datestr) < datenum(date_start)
                        continue
                    end
                    if datenum(picture_datestr) > datenum(date_end)
                        picture_limit_exceeded = true;
                        break
                    end
%                     if pictures(1).datenum > ()
 
                    % for pics_i = 1:length(pictures)
                    %     pictures(pics_i).name_orig = pictures(pics_i).name;
                    %     % pictures(pics_i).name = [path_session_folder pictures(pics_i).name];
                    % end
                    if ~exist('files_images', 'var')
                        files_images = pictures';
                    else
                        files_images = [files_images, pictures'];
                    end                 
                end
%                 if picture_limit_exceeded 
%                     break
%                 end
              
                % % ordeno por fecha
                % size_files_images = length(files_images);
                % % fprintf('Sorting %d files in %s\n', size_files_images, path_sessions)
                % fprintf('Adding datenum from exif to %d files\n', size_files_images)
                % for t=1:size_files_images
                %     full_name_image = files_images(t).name;
                %     info = imfinfo(full_name_image);
                %     date = info.DigitalCamera.DateTimeOriginal;
                %     files_images(t).datenum = datenum(datetime(date,'InputFormat','yyyy:MM:dd H:m:s'));
                % end
                % [tmp ind]=sort([files_images.datenum]);
                % files = files_images(ind);
                files = files_images;
            end
        else
            files=dir([path_images '*.jpg']);
            clear files_images
            videoId = ['w' session];
            wsname = [base_output_path '\u18_workspaces\' videoId '.mat'];
        end
        
        
        fprintf('Session id: %s\n', videoId)    
        fprintf('Session datestr: %s\n', datestr(session_datenum, 'yyyy-mm-dd HH:MM'))
        
        
%         path_processed = 'D:\Users\an\experimento-usb-interferometro\graficada\';
%         path_output = 'D:\Users\an\experimento-usb-interferometro\videos\';
%         pathToFigures = 'D:\Users\an\experimento-usb-interferometro\figures\';            
%         path_sessions_not_used = 'D:\Users\an\experimento-usb-interferometro\sessions-not-with-enough-rotations\';

        path_processed = [base_output_path '\graficada\']';
        path_output = [base_output_path '\videos\'];
        pathToFigures = [base_output_path '\figures\'];            
        path_sessions_not_used = [base_output_path '\sessions-not-with-enough-rotations\'];
        
        nfiles=length(files);
        if nfiles < 100
            fprintf('Menos de 100 fotos. Ignorando carpeta: %s\n\n\n', session)
            % movefile(path_images, path_sessions_not_used)
            continue
        end  
        
        if day_session
            fconf = [path_sessions videoId '.csv'];
        else
            fconf = [path_images videoId '.csv'];
        end
        if exist(fconf, 'file')
            conf = readtable(fconf);   
            
            fields = fieldnames(conf);
            for f=1:length(fields)
                if ~strcmp(fields{f},'Properties')
                    eval([fields{f} '=conf.(fields{f});'])
                end
            end
            % clear lineaPreferida lineaPreferidaAdjunta
        else
            conf.none = 0;
            conf = struct2table(conf);
        end   
               
        if exist('onlyLoadConfig', 'var') && onlyLoadConfig == true
            return
        end

        path_images_old = path_images;
        path_sessions_old = path_sessions;

%         fconf = [path_images videoId '.csv'];
%         if exist(fconf, 'file')
%             conf = readtable(fconf);   
%             fields = fieldnames(conf);
%             fprintf('Archivo de configuracion:\n')
%             for f=1:length(fields)
% 
%                 if ~strcmp(fields{f},'Properties')
%                     eval([fields{f} '=conf.(fields{f})']);
%     %                 fprintf('%s = %s:\n', fields{f},eval('conf.(fields{f})'))
%                 end
%             end
%         end       

        stepFrames = 1;
%         filterDiskSize = 5;
%         rotationStop = true;
        rotationAngle = 88;
        rotating_session = 1;
        saveFile = true;
%         figureCreated = true;        
        
        force_reprocess = false;
        if isfield(processing_session, 'force_reprocess')
            force_reprocess = processing_session.force_reprocess;
        end
        
        workspace_loaded = 0;
        if exist(wsname, 'file') && ~force_reprocess
            % if ~day_session
                try
                    load(wsname, '-regexp', '^(?!ses|tim|conf|videoId|y_scale|package_name|date_start|date_end|day_session|y_scale|processing_session|pathToFigures)...')
                    workspace_loaded = 1;
                catch
                    workspace_loading_failed=1
                end
            % end
        end
        if workspace_loaded == 0
            onlyLoadConfig = false;
            ignore_folder = false;
            % clear lineaPreferida lineaPreferidaAdjunta

            u18_analisis_fotos
            if ignore_folder
                % fprintf('Moving folder to %s\n', path_sessions_not_used)
                % movefile(path_images, path_sessions_not_used)
                continue
            end
        % u18_makevideo
        end

       
        % lineaPreferida=2;
        % lineaPreferidaAdjunta=3;
        suavizar=false;
        ajustarDefault = true;
        % if day_session
        %     ajustarDefault = false;
        % end
        % ajustarDefault = false;
        force_choose_line = true;
        % saveLogFile('init')
        graficoAzimuth = true;
        limitesGraficasPromediada = false;
        rotacionini = 1;
        
        % puntosSeparacionFranjas=1000;
        puntosSeparacionFranjasMin=800;
        % initial_point = 117;
        path_images = path_images_old;
        path_sessions = path_sessions_old;
        plot_rotations = false;
        session_duration_min = 30;
        
        
        if ~exist('rotating_session', 'var')
            answer = input('Rotating session? 0/1:');
        end
        
%         if ~isfield(table2struct(conf), 'rotating_session')
%             conf.rotating_session = rotating_session ;
%             writetable(conf, fconf);          
%         end          

        % clear lineaPreferida lineaPreferidaAdjunta
        u18_plots
        % a=1

        % reply = input(['Move ' path_images_old ' to ' '[Y/n]?'],'s');
        % if isempty(reply)
        %     reply = 'Y';
        % end
        % if reply == 'Y'
        %   if s < length(sessionsx)
        %     load gong.mat;
        %     sound(y);
        %     movefile(path_images, path_processed)
        %   end
        % end

        if day_session
            break
        end
    end
end