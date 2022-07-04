% ordering package information

clear usb_sessions

global package_name
global processing_session

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
REMOVE_DRIFT = false;
SAVE_TXT_DATA = true;
REMOVE_OUTLIERS = false;

load_sessions

% load_old_sessions

% usb_sessions es la definicion de todas las sesiones

%%%%%%%%%%%%%%%%%%%

% Filtro de las que quiero procesar
% En usb_session están todas las sesiones definidas
process_sessions = [
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
    '2200702-2200704-aire-vidrio-vidrio'
];

for sindex=1:size(process_sessions, 1)
    for uindex=1:length(usb_sessions)
        if ~ strcmp(usb_sessions(uindex).name, process_sessions(sindex,:))
            continue
        end

        processing_session = usb_sessions(uindex);
        if ~isfield(processing_session, 'day_session')
            processing_session.day_session = DAY_SESSION;
        end
        if ~isfield(processing_session, 'y_scale')
            processing_session.y_scale = Y_SCALE;
        end
        if ~isfield(processing_session, 'ignore_folder')
            processing_session.ignore_folder = IGNORE_FOLDER;
        end        
        if ~isfield(processing_session, 'ignore_datetime')
            processing_session.ignore_datetime = IGNORE_DATETIME;
        end
        if ~isfield(processing_session, 'makeVideo')
            processing_session.makeVideo = MAKE_VIDEO;
        end        
        if ~isfield(processing_session, 'force_reprocess')
            processing_session.force_reprocess = FORCE_REPROCESS;
        end
        if ~isfield(processing_session, 'minpeakdistance')
            processing_session.minpeakdistance = MIN_PEAK_DISTANCE;
        end
        if ~isfield(processing_session, 'smooth_num_points')
            processing_session.smooth_num_points = SMOOTH_NUM_POINTS;
        end
        if ~isfield(processing_session, 'filterDiskSize')
            processing_session.filterDiskSize = FILTER_DISK_SIZE;
        end
        if ~isfield(processing_session, 'remove_drift')
            processing_session.remove_drift = REMOVE_DRIFT ;
        end       
        if ~isfield(processing_session, 'saveTxtData')
            processing_session.saveTxtData = SAVE_TXT_DATA ;
        end       
        if ~isfield(processing_session, 'removeOutliers')
            processing_session.removeOutliers = REMOVE_OUTLIERS ;
        end            
        
        
        package_name = processing_session.name;
        date_start = processing_session.date_start;
        date_end = processing_session.date_end;
        day_session = processing_session.day_session;
        y_scale = processing_session.y_scale;

        u18w_general
    end
end