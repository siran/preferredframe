% ordering package information

clear usb_sessions
recycle('on')

global package_name
global processing_session
% global path_images

usb_sessions = struct();

% % DEFAULTS
DAY_SESSION = false;
Y_SCALE = false;
IGNORE_FOLDER = {};
IGNORE_DATETIME = {};
MAKE_VIDEO = false;
FORCE_REPROCESS = false;
MIN_PEAK_DISTANCE = 60;
SMOOTH_NUM_POINTS = 20;
FILTER_DISK_SIZE = 10;
REMOVE_DRIFT = true;
SAVE_TXT_DATA = false;
REMOVE_OUTLIERS = false;
ERROR_BARS = true;
PCT_VALID_DATA = .3;

load_sessions

% load_old_sessions

% usb_sessions es la definicion de todas las sesiones

%%%%%%%%%%%%%%%%%%%

% Filtro de las que quiero procesar
% En usb_session están todas las sesiones definidas
process_sessions = {
%     '200515-200531-con-deriva'
%     '200601-200625-con-deriva'
%     '20180921-1730-greaves'
%     '20180921-greaves-comparacion1'
%     '20200321-2030-greaves'
%     '2022-06-17 vidrio-vidrio'
%     '2022-06-17 vidrio-vidrio-raw'
%     '2022-06-22-vidrio-vidrio-nivelado'
%     'aire-aire-paralelo-20200515-20200517'
%     '220630-220702-aire-vidrio-vidrio'
%     '2200702-2200704-aire-vidrio-vidrio'
%     '180914-180915-vidrio-aire'
%     '190320-190325-vidrio-aire-reanalisis-220717'
%     '220706-220706-vidrio-vidrio-aire'
%     '220805-220815-especial-greaves'
%     '200309-200310'
%     '200320-200324'
%     '200515 - 200527'
%     '200619-200623'
%     '200701-2007002'
%     '200711-200716'
%     '200810-200820'
%     '200917-200919'
%     '201009-201014'
    

%     '201114-201117'
%     '201119-201123'
%     '200217-'
%     '200210-200303'
%     '200221-'
%       '200229-200303'

%     '210131-210222'te
    
%     '210307-210309' 
%     '210327-210408'
%     '210428-210525'
%     '220617-220621'
%     '220702-220706'
%     '180818-181216'
%     '180920-180926'
%     '181008-181012'
%     '191001-191006'
%     '191016-191125'
%     '200221-200228-partial-reprocesss--req-edo'
    % '2021-04--req-edo'
    '2020-02-27--2020-03-24--paper-2'

};

for sindex=1:size(process_sessions, 1)
    for uindex=1:length(usb_sessions)
        if isempty(usb_sessions(uindex).name)
            fprintf('usb_sessions(%d) is empty. continue.\n', uindex)
            continue
        end
        fprintf('    %s =? %s\n', usb_sessions(uindex).name, process_sessions{sindex,:})
        if ~ strcmp(usb_sessions(uindex).name, process_sessions{sindex,:})
            continue
        end
        fprintf('\n\nProcessing package: %s \n', usb_sessions(uindex).name)

        processing_session = usb_sessions(uindex);
        if ~isfield(processing_session, 'day_session') || isempty(processing_session.day_session)
            processing_session.day_session = DAY_SESSION;
        end
        if ~isfield(processing_session, 'y_scale') || isempty(processing_session.y_scale)
            processing_session.y_scale = Y_SCALE;
        end  
        if ~isfield(processing_session, 'ignore_folder') || isempty(processing_session.ignore_folder)
            processing_session.ignore_folder = IGNORE_FOLDER;
        end        
        if ~isfield(processing_session, 'ignore_datetime') || isempty(processing_session.ignore_datetime)
            processing_session.ignore_datetime = IGNORE_DATETIME;
        end
        if ~isfield(processing_session, 'makeVideo') || isempty(processing_session.makeVideo)
            processing_session.makeVideo = MAKE_VIDEO;
        end        
        if ~isfield(processing_session, 'force_reprocess') || isempty(processing_session.force_reprocess)
            processing_session.force_reprocess = FORCE_REPROCESS;
        end
        if ~isfield(processing_session, 'minpeakdistance') || isempty(processing_session.minpeakdistance)
            processing_session.minpeakdistance = MIN_PEAK_DISTANCE;
        end
        if ~isfield(processing_session, 'smooth_num_points') || isempty(processing_session.smooth_num_points)
            processing_session.smooth_num_points = SMOOTH_NUM_POINTS;
        end
        if ~isfield(processing_session, 'filterDiskSize') || isempty(processing_session.filterDiskSize)
            processing_session.filterDiskSize = FILTER_DISK_SIZE;
        end
        if ~isfield(processing_session, 'remove_drift') || isempty(processing_session.remove_drift)
            processing_session.remove_drift = REMOVE_DRIFT ;
        end       
        if ~isfield(processing_session, 'saveTxtData') || isempty(processing_session.saveTxtData)
            processing_session.saveTxtData = SAVE_TXT_DATA ;
        end       
        if ~isfield(processing_session, 'removeOutliers') || isempty(processing_session.removeOutliers)
            processing_session.removeOutliers = REMOVE_OUTLIERS ;
        end           
        if ~isfield(processing_session, 'error_bars') || isempty(processing_session.error_bars)
            processing_session.error_bars = ERROR_BARS ;
        end
        if ~isfield(processing_session, 'pct_valid_data') || isempty(processing_session.pct_valid_data)
            processing_session.pct_valid_data = PCT_VALID_DATA ;
        end     
        
        
        
        package_name = processing_session.name;
        date_start = processing_session.date_start;
        date_end = processing_session.date_end;
        day_session = processing_session.day_session;
        y_scale = processing_session.y_scale;
        force_reprocess = processing_session.force_reprocess;

        u18w_general
    end
end