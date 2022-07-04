index = length(usb_sessions)+1;
usb_sessions(index).name = '20180826-1400-no-rotation';
usb_sessions(index).date_start = '2018-08-26 14:00';
usb_sessions(index).date_end = '2019-11-02 03:30';
usb_sessions(index).day_session = false;
usb_sessions(index).y_scale = false;
usb_sessions(index).ignore_datetime = {};
usb_sessions(index).makeVideo = true;
usb_sessions(index).force_reprocess = false;
usb_sessions(index).minpeakdistance = 60;
usb_sessions(index).smooth_num_points = 20;
usb_sessions(index).filterDiskSize = 10;
usb_sessions(index).rotating_session = false;

% aire-aire-perpendicular 2020-03-09 - 2020-03-10
index = length(usb_sessions)+1;
usb_sessions(index).name = 'aire-aire-perpen-20200309-20200310-day';
usb_sessions(index).date_start = '2020-03-09 21:30';
usb_sessions(index).date_end = '2020-03-10 19:30';
usb_sessions(index).day_session = true;
usb_sessions(index).y_scale = true;

% aire-aire-perpendicular 2020-03-09 - 2020-03-10
index = length(usb_sessions)+1;
usb_sessions(index).name = 'aire-aire-paralelo-20200515-20200517-day';
usb_sessions(index).date_start = '2020-05-15 18:30';
usb_sessions(index).date_end = '2020-05-17 09:29';
usb_sessions(index).day_session = true;
usb_sessions(index).y_scale = true;

% aire-aire-perpendicular 2020-05-09 - 2020-03-10
index = length(usb_sessions)+1;
usb_sessions(index).name = 'aire-aire-perpen-20200517-20200518-day';
usb_sessions(index).date_start = '2020-05-17 11:00';
usb_sessions(index).date_end = '2020-05-18 09:29';
usb_sessions(index).day_session = true;
usb_sessions(index).y_scale = false;

% aire-aire-perpendicular 2020-05-09 - 2020-03-10
index = length(usb_sessions)+1;
usb_sessions(index).name = 'aire-vidro-doblepaso-20200810-20200815-day';
usb_sessions(index).date_start = '2020-08-10 13:00';
usb_sessions(index).date_end = '2020-08-15 11:30';
usb_sessions(index).day_session = true;
usb_sessions(index).y_scale = false;

% aire-aire-perpendicular 2020-05-09 - 2020-03-10
index = length(usb_sessions)+1;
usb_sessions(index).name = 'aire-vidro-doblepaso-20200810-20200815-day-2x';
usb_sessions(index).date_start = '2020-08-10 13:00';
usb_sessions(index).date_end = '2020-08-15 11:30';
usb_sessions(index).day_session = true;
usb_sessions(index).y_scale = true;

index = length(usb_sessions)+1;
usb_sessions(index).name = 'aire-vidro-doblepaso-20201009-20201013-day-2x';
usb_sessions(index).date_start = '2020-10-09 11:00';
usb_sessions(index).date_end = '2020-10-13 23:30';
usb_sessions(index).day_session = true;
usb_sessions(index).y_scale = true;

index = length(usb_sessions)+1;
usb_sessions(index).name = 'aire-vidro-doblepaso-20201009-20201013-day';
usb_sessions(index).date_start = '2020-10-09 11:00';
usb_sessions(index).date_end = '2020-10-13 23:30';
usb_sessions(index).day_session = true;
usb_sessions(index).y_scale = false;

index = length(usb_sessions)+1;
usb_sessions(index).name = 'aire-vidro-doblepaso-20201009-20201013';
usb_sessions(index).date_start = '2020-10-09 12:00';
usb_sessions(index).date_end = '2020-10-13 23:30';
usb_sessions(index).day_session = false;
usb_sessions(index).y_scale = false;

index = length(usb_sessions)+1;
usb_sessions(index).name = 'aire-vidro-doblepaso-20210110-20211012';
usb_sessions(index).date_start = '2021-01-10 16:30';
usb_sessions(index).date_end = '2021-01-12 12:00';
usb_sessions(index).day_session = false;
usb_sessions(index).y_scale = false;

index = length(usb_sessions)+1;
usb_sessions(index).name = '210119-211020-aire-vidro-doblepaso';
usb_sessions(index).date_start = '2021-01-19 00:00';
usb_sessions(index).date_end = '2021-01-20 23:30';
usb_sessions(index).day_session = false;
usb_sessions(index).y_scale = false;

index = length(usb_sessions)+1;
usb_sessions(index).name = '210130-210208-aire-vidro-doblepaso';
usb_sessions(index).date_start = '2021-02-12 08:00';
usb_sessions(index).date_end = '2021-02-17 17:30';
usb_sessions(index).day_session = false;
usb_sessions(index).y_scale = false;
usb_sessions(index).ignore_datetime = {...
    '2021-02-04 08:00', ...
    '2021-02-05 15:00', '2021-02-05 16:00', '2021-02-05 16:30', '2021-02-05 17:00', ...
    '2021-02-06 09:00', '2021-02-06 09:30', '2021-02-06 10:00', ...
    '2021-02-07 06:00'...
    };

index = length(usb_sessions)+1;
usb_sessions(index).name = '210130-1630-test-corte-perp';
usb_sessions(index).date_start = '2021-01-30 16:30';
usb_sessions(index).date_end = '2021-01-30 16:30';
usb_sessions(index).day_session = false;
usb_sessions(index).y_scale = false;
usb_sessions(index).ignore_datetime = {};
usb_sessions(index).makeVideo = true;

index = length(usb_sessions)+1;
usb_sessions(index).name = '210119-1900-test-corte-perp';
usb_sessions(index).date_start = '2021-01-19 19:00';
usb_sessions(index).date_end = '2021-01-19 19:00';
usb_sessions(index).day_session = false;
usb_sessions(index).y_scale = false;
usb_sessions(index).ignore_datetime = {};
usb_sessions(index).makeVideo = true;

index = length(usb_sessions)+1;
usb_sessions(index).name = '210307-210309-aire-vidro-doblepaso';
usb_sessions(index).date_start = '2021-03-07 15:30';
% usb_sessions(index).date_start = '2021-03-07 16:30';
usb_sessions(index).date_start = '2021-03-07 22:00';
usb_sessions(index).date_end = '2021-03-09 11:00';
usb_sessions(index).day_session = false;
usb_sessions(index).y_scale = false;
usb_sessions(index).ignore_datetime = {};
usb_sessions(index).makeVideo = false;
usb_sessions(index).force_reprocess = true;

index = length(usb_sessions)+1;
usb_sessions(index).name = '210327-210328-aire-vidrio-doblepaso';
usb_sessions(index).date_start = '2021-03-27 11:00';
usb_sessions(index).date_end = '2021-03-28 15:30';
usb_sessions(index).day_session = false;
usb_sessions(index).y_scale = false;
usb_sessions(index).ignore_datetime = {};
usb_sessions(index).makeVideo = true;
usb_sessions(index).minpeakdistance = 50;
usb_sessions(index).force_reprocess = true;
usb_sessions(index).smooth_num_points = 30;

index = length(usb_sessions)+1;
usb_sessions(index).name = '210202-1430-aire-vidrio-doblepaso';
usb_sessions(index).date_start = '2021-02-02 14:30';
usb_sessions(index).date_end = '2021-02-02 14:30';
usb_sessions(index).day_session = false;
usb_sessions(index).y_scale = false;
usb_sessions(index).ignore_datetime = {};
usb_sessions(index).makeVideo = true;
usb_sessions(index).force_reprocess = true;

index = length(usb_sessions)+1;
usb_sessions(index).name = '210202-2100-aire-vidrio-doblepaso';
usb_sessions(index).date_start = '2021-02-02 21:00';
usb_sessions(index).date_end = '2021-02-02 21:00';
usb_sessions(index).day_session = false;
usb_sessions(index).y_scale = false;
usb_sessions(index).ignore_datetime = {};
usb_sessions(index).makeVideo = true;
usb_sessions(index).force_reprocess = true;

process_sessions = [
%     'aire-aire-perpen-20200309-20200310-day'
%     'aire-aire-paralelo-20200515-20200517-day'
%     'aire-aire-perpen-20200517-20200518-day'
%     'aire-vidro-doblepaso-20200810-20200815-day'
%     'aire-vidro-doblepaso-20200810-20200815-day-2x'
%     'aire-vidro-doblepaso-20201009-20201013-day-2x'
%     'aire-vidro-doblepaso-20201009-20201013-day'
% 'aire-vidro-doblepaso-20201009-20201013'
%    'aire-vidro-doblepaso-20210110-20211012'
% '21210119-21211020-aire-vidro-doblepaso'
% '210130-210208-aire-vidro-doblepaso'
% '210130-1630-test'
% '210130-1630-test-corte-perp'
% '210119-1900-test-corte-perp'
% '210307-210309-aire-vidro-doblepaso'
% '210327-210328-aire-vidrio-doblepaso'
% '210202-1430-aire-vidrio-doblepaso'
% '210202-2100-aire-vidrio-doblepaso'
% '180818-181216-con-deriva'
% '180818-181216'
% '180818-181216-fix'
% '20180826-1400-no-rotation'
% '20191101-20191124'
% '20191001-20191019'
% '20190901-20190922'
% '20190923-20190930'
% '20210426-20210430-MM'
% '20210430-MM'
% '20210501-MM-robert'
% '20210520-MM'
% '20210426-greaves'
% '190910-190930'
% '200917-200919'
% '190802-190804'
% '200810-200820',
% '200810-200820-con-deriva'
% '190910-190930-con-deriva'
];