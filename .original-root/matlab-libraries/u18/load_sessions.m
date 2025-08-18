index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = 'test-200210-200303-fig6-stellar';
usb_sessions(index).date_start = '2020-02-21 00:00';
usb_sessions(index).remove_drift = true;
usb_sessions(index).day_session = false ;
usb_sessions(index).rotating_session = true;
usb_sessions(index).force_reprocess = false;
% usb_sessions(index).date_end = '2020-02-21 00:30';
usb_sessions(index).date_end = '2020-02-24 00:00';
usb_sessions(index).force_reprocess = false;
usb_sessions(index).add_hours = -4;
usb_sessions(index).ignore_datetime = {'2020-02-10 15:30', '2020-02-14 16:30', ...
    '2020-02-15 15:00', ...
    '2020-02-15 15:30', ...
    '2020-02-15 15:30', ...
    '2020-02-17 15:00', '2020-02-17 15:30','2020-02-17 16:00',...
    '2020-02-17 16:30','2020-02-17 17:00','2020-02-17 17:30'};

index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '200210-200303-fig6-stellar';
usb_sessions(index).date_start = '2020-02-21 00:00';
usb_sessions(index).remove_drift = false;
usb_sessions(index).day_session = false ;
usb_sessions(index).rotating_session = true;
usb_sessions(index).force_reprocess = false;
usb_sessions(index).date_end = '2020-03-03 18:00';
% usb_sessions(index).date_end = '2020-02-24 00:00';
usb_sessions(index).force_reprocess = false;
usb_sessions(index).add_hours = -4;
usb_sessions(index).ignore_datetime = {'2020-02-10 15:30', '2020-02-14 16:30', ...
    '2020-02-15 15:00', ...
    '2020-02-15 15:30', ...
    '2020-02-15 15:30', ...
    '2020-02-17 15:00', '2020-02-17 15:30','2020-02-17 16:00',...
    '2020-02-17 16:30','2020-02-17 17:00','2020-02-17 17:30'};

index = length(usb_sessions)+1;
usb_sessions(index).name = '200701-200731';
usb_sessions(index).date_start = '2020-06-30 00:00';
usb_sessions(index).date_start = '2020-07-01 07:00';
% usb_sessions(index).ignore_datetime = {'2020-06-01 18:00', '2020-06-09 13:00','2020-06-19 12:00'};
usb_sessions(index).date_end = '2020-07-31 23:30';
usb_sessions(index).remove_drift = true;
usb_sessions(index).day_session = false ;
usb_sessions(index).rotating_session = true;
usb_sessions(index).force_reprocess = false;
usb_sessions(index).add_hours = -4;


index = length(usb_sessions)+1;
usb_sessions(index).name = '200601-200630-req-edo';
usb_sessions(index).date_start = '2020-06-01 00:00';
usb_sessions(index).date_start = '2020-06-01 18:00';
usb_sessions(index).date_start = '2020-06-09 13:00';
usb_sessions(index).date_start = '2020-06-19 12:00';
usb_sessions(index).ignore_datetime = {'2020-06-01 18:00', '2020-06-09 13:00','2020-06-19 12:00'};
usb_sessions(index).remove_drift = true;
usb_sessions(index).day_session = false ;
usb_sessions(index).rotating_session = true;
usb_sessions(index).force_reprocess = false;
usb_sessions(index).date_end = '2020-06-30 23:30';
usb_sessions(index).force_reprocess = false;
usb_sessions(index).add_hours = -4;

index = length(usb_sessions)+1;
usb_sessions(index).name = '201121-201124-fig8-sun-moon-cmbr-sessions';
usb_sessions(index).date_start = '2020-11-21 00:00';
usb_sessions(index).remove_drift = true;
usb_sessions(index).day_session = false ;
usb_sessions(index).rotating_session = true;
usb_sessions(index).force_reprocess = false;
% usb_sessions(index).date_end = '2020-03-03 18:00';
usb_sessions(index).date_end = '2020-11-24 00:00';
usb_sessions(index).force_reprocess = false;

index = length(usb_sessions)+1;
usb_sessions(index).name = '200521-200524-fig7-sun-moon-cmbr-sessions';
usb_sessions(index).date_start = '2020-05-21 00:00';
usb_sessions(index).remove_drift = true;
usb_sessions(index).day_session = false ;
usb_sessions(index).rotating_session = true;
usb_sessions(index).force_reprocess = false;
% usb_sessions(index).date_end = '2020-03-03 18:00';
usb_sessions(index).date_end = '2020-05-24 00:00';
usb_sessions(index).force_reprocess = false;

index = length(usb_sessions)+1;
usb_sessions(index).name = '200221-200224-fig6-sun-moon-cmbr-sessions';
usb_sessions(index).date_start = '2020-02-21 00:00';
usb_sessions(index).remove_drift = true;
usb_sessions(index).day_session = false ;
usb_sessions(index).rotating_session = true;
usb_sessions(index).force_reprocess = false;
usb_sessions(index).date_end = '2020-03-03 18:00';
usb_sessions(index).date_end = '2020-02-24 00:00';
usb_sessions(index).force_reprocess = false;
usb_sessions(index).ignore_datetime = {'2020-02-10 15:30', '2020-02-14 16:30', ...
    '2020-02-15 15:00', ...
    '2020-02-15 15:30', ...
    '2020-02-15 15:30', ...
    '2020-02-17 15:00', '2020-02-17 15:30','2020-02-17 16:00',...
    '2020-02-17 16:30','2020-02-17 17:00','2020-02-17 17:30'};


index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '200210-200303-fig6-sun-moon-cmbr';
usb_sessions(index).date_start = '2020-02-21 00:00';
usb_sessions(index).remove_drift = false;
usb_sessions(index).day_session = true ;
usb_sessions(index).rotating_session = false;
usb_sessions(index).force_reprocess = false;
usb_sessions(index).date_end = '2020-03-03 18:00';
usb_sessions(index).date_end = '2020-02-24 00:00';
usb_sessions(index).force_reprocess = false;
usb_sessions(index).ignore_datetime = {'2020-02-10 15:30', '2020-02-14 16:30', ...
    '2020-02-15 15:00', ...
    '2020-02-15 15:30', ...
    '2020-02-15 15:30', ...
    '2020-02-17 15:00', '2020-02-17 15:30','2020-02-17 16:00',...
    '2020-02-17 16:30','2020-02-17 17:00','2020-02-17 17:30'};



index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '200226-partial-reprocesss--req-edo-day_session-sun,moon';
usb_sessions(index).date_start= '2020-02-26';
usb_sessions(index).date_end = '2020-02-27';
usb_sessions(index).force_reprocess = false;
usb_sessions(index).saveTxtData = false ;
usb_sessions(index).day_session = true ;
usb_sessions(index).remove_drift = false;
usb_sessions(index).rotating_session = false;

index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '200225-200226-partial-reprocesss--req-edo-day_session-sun,moon';
usb_sessions(index).date_start= '2020-02-25';
usb_sessions(index).date_end = '2020-02-26';
usb_sessions(index).force_reprocess = false;
usb_sessions(index).saveTxtData = false ;
usb_sessions(index).day_session = true ;
usb_sessions(index).remove_drift = false;
usb_sessions(index).rotating_session = false;

index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '200221-200228-partial-reprocesss--req-edo-day_session';
usb_sessions(index).date_start = '2020-02-21';
% usb_sessions(index).date_start = '2020-02-12 01:30';
% usb_sessions(index).date_start = '2020-02-12 23:30';
% usb_sessions(index).date_start = '2020-02-13 03:00';
% usb_sessions(index).date_start = '2020-02-17 17:00';
% usb_sessions(index).date_start = '2020-02-25 14:30';
% usb_sessions(index).date_start= '2020-02-22 01:00';
% usb_sessions(index).date_start= '2020-02-22 18:30';
% usb_sessions(index).date_start= '2020-02-23 00:30';
usb_sessions(index).date_start= '2020-02-23 06:30';
usb_sessions(index).date_end = '2020-02-28';
usb_sessions(index).force_reprocess = false;
usb_sessions(index).saveTxtData = false ;
usb_sessions(index).day_session = true ;
usb_sessions(index).remove_drift = false;
usb_sessions(index).rotating_session = false;
usb_sessions(index).ignore_datetime = {'2020-02-17 15:00', '2020-02-17 15:30','2020-02-17 16:00',...
    '2020-02-17 16:30','2020-02-17 17:00','2020-02-17 17:30'};

index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '2020-02-27--2020-03-24--paper-2-day_session';
usb_sessions(index).date_start = '2020-03-05';
% usb_sessions(index).date_start = '2020-02-29 18:30';
usb_sessions(index).date_end = '2020-03-08 17:00';
usb_sessions(index).force_reprocess = false;
usb_sessions(index).saveTxtData = false ;
usb_sessions(index).day_session = true ;
usb_sessions(index).remove_drift = false;
usb_sessions(index).rotating_session = false;


index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '2020-02-27--2020-03-24--paper-2';
usb_sessions(index).date_start = '2020-02-27';
usb_sessions(index).date_start = '2020-02-28 23:30';
usb_sessions(index).date_start = '2020-02-29 18:00';
usb_sessions(index).date_end = '2020-03-25';
usb_sessions(index).date_end = '2020-03-08 17:00';
usb_sessions(index).force_reprocess = false;
usb_sessions(index).saveTxtData = true ;

index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '2021-04--req-edo';
usb_sessions(index).date_start = '2021-04-01 18:30';
usb_sessions(index).date_end = '2021-04-30 23:59';
usb_sessions(index).force_reprocess = true;
usb_sessions(index).saveTxtData = true ;

index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '200221-200228-partial-reprocesss--req-edo';
usb_sessions(index).date_start = '2020-02-21';
% usb_sessions(index).date_start = '2020-02-12 01:30';
% usb_sessions(index).date_start = '2020-02-12 23:30';
% usb_sessions(index).date_start = '2020-02-13 03:00';
% usb_sessions(index).date_start = '2020-02-17 17:00';
% usb_sessions(index).date_start = '2020-02-25 14:30';
% usb_sessions(index).date_start= '2020-02-22 01:00';
% usb_sessions(index).date_start= '2020-02-22 18:30';
% usb_sessions(index).date_start= '2020-02-23 00:30';
% usb_sessions(index).date_start= '2020-02-23 06:30';
usb_sessions(index).date_end = '2020-02-28';
usb_sessions(index).force_reprocess = true;
usb_sessions(index).saveTxtData = true ;
usb_sessions(index).ignore_datetime = {'2020-02-17 15:00', '2020-02-17 15:30','2020-02-17 16:00',...
    '2020-02-17 16:30','2020-02-17 17:00','2020-02-17 17:30'};

index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '191016-191125';
usb_sessions(index).date_start = '2019-10-16';
usb_sessions(index).date_start = '2019-10-17 03:30';
usb_sessions(index).date_end = '2019-11-25';
usb_sessions(index).force_reprocess = true;
usb_sessions(index).ignore_date = {'2019-10-17'};

index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '191001-191006';
usb_sessions(index).date_start = '2019-10-01';
usb_sessions(index).date_start = '2019-10-04 10:00';
usb_sessions(index).date_end = '2019-10-06';
usb_sessions(index).force_reprocess = true;
usb_sessions(index).ignore_datetime = {};

index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '180920-180926';
usb_sessions(index).date_start = '2018-09-20';
usb_sessions(index).date_end = '2018-09-26';
usb_sessions(index).force_reprocess = true;
usb_sessions(index).ignore_datetime = {};


index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '220702-220706';
usb_sessions(index).date_start = '2022-07-02 16:30';
usb_sessions(index).date_end = '2022-07-06 07:00';
usb_sessions(index).force_reprocess = true;
usb_sessions(index).ignore_datetime = {};

index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '220617-220621';
usb_sessions(index).date_start = '2022-06-22 16:00';
usb_sessions(index).date_end = '2022-07-02';
usb_sessions(index).force_reprocess = true;
usb_sessions(index).ignore_datetime = {};

index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '220617-220621';
usb_sessions(index).date_start = '2022-06-17 11:00';
usb_sessions(index).date_end = '2022-06-21';
usb_sessions(index).force_reprocess = true;
usb_sessions(index).ignore_datetime = {};

index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '210428-210525';
usb_sessions(index).date_start = '2021-04-28';
usb_sessions(index).date_start = '2021-05-07 13:00';
usb_sessions(index).date_end = '2021-05-25';
usb_sessions(index).force_reprocess = true;
usb_sessions(index).ignore_datetime = {};

index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '210327-210408';
usb_sessions(index).date_start = '2021-03-27';
usb_sessions(index).date_end = '2021-04-09';
usb_sessions(index).force_reprocess = true;
usb_sessions(index).ignore_datetime = {};

index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '210327-210408';
usb_sessions(index).date_start = '2021-03-27';
usb_sessions(index).date_end = '2021-04-09';
usb_sessions(index).force_reprocess = true;
usb_sessions(index).ignore_datetime = {};

index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '210307-210309';
usb_sessions(index).date_start = '2021-03-07 15:00';
usb_sessions(index).date_end = '2021-03-09';
usb_sessions(index).force_reprocess = true;
usb_sessions(index).ignore_datetime = {};

index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '200210-200303';
usb_sessions(index).date_start = '2020-02-10 15:30';
usb_sessions(index).date_start = '2020-02-12 01:30';
usb_sessions(index).date_start = '2020-02-12 23:30';
usb_sessions(index).date_start = '2020-02-13 03:00';
usb_sessions(index).date_start = '2020-02-17 17:00';
usb_sessions(index).date_start = '2020-02-25 14:30';
% usb_sessions(index).date_start= '2020-02-22 01:00';
% usb_sessions(index).date_start= '2020-02-22 18:30';
% usb_sessions(index).date_start= '2020-02-23 00:30';
% usb_sessions(index).date_start= '2020-02-23 06:30';
usb_sessions(index).date_end = '2020-03-03 18:00';
usb_sessions(index).force_reprocess = false;
usb_sessions(index).ignore_datetime = {'2020-02-17 15:00', '2020-02-17 15:30','2020-02-17 16:00',...
    '2020-02-17 16:30','2020-02-17 17:00','2020-02-17 17:30'};


index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '210131-210222';
usb_sessions(index).date_start = '2021-01-31 06:30';
usb_sessions(index).date_end = '2021-02-22';
usb_sessions(index).force_reprocess = true;
usb_sessions(index).ignore_datetime = {};

index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '201119-201123';
usb_sessions(index).date_start = '2020-11-19';
usb_sessions(index).date_start = '2020-11-22 22:00';
usb_sessions(index).date_end = '2020-11-23';
usb_sessions(index).force_reprocess = true;
usb_sessions(index).ignore_datetime = {};

index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '201114-201117';
usb_sessions(index).date_start = '2020-11-14 15:00';
usb_sessions(index).date_end = '2020-11-18';
usb_sessions(index).force_reprocess = true;
usb_sessions(index).ignore_datetime = {};


index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '201009-201014';
usb_sessions(index).date_start = '2020-10-09 11:00';
usb_sessions(index).date_end = '2020-10-14';
usb_sessions(index).force_reprocess = true;
usb_sessions(index).ignore_datetime = {};

index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '200917-200919';
usb_sessions(index).date_start = '2020-09-17 11:00';
usb_sessions(index).date_end = '2020-09-20';
usb_sessions(index).force_reprocess = true;
usb_sessions(index).ignore_datetime = {};

index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '200810-200820';
usb_sessions(index).date_start = '2020-08-10 13:30';
usb_sessions(index).date_start = '2020-08-10 20:00';
usb_sessions(index).date_end = '2020-08-21';
usb_sessions(index).force_reprocess = true;
usb_sessions(index).ignore_datetime = {};


index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '200711-200716';
usb_sessions(index).date_start = '2020-07-11 12:30';
usb_sessions(index).date_end = '2020-07-17';
usb_sessions(index).force_reprocess = true;
usb_sessions(index).ignore_datetime = {};


index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '200701-2007002';
usb_sessions(index).date_start = '2020-07-01';
usb_sessions(index).date_end = '2020-07-03';
usb_sessions(index).force_reprocess = true;
usb_sessions(index).ignore_datetime = {};

index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '200619-200623';
usb_sessions(index).date_start = '2020-06-19 13:30';
usb_sessions(index).date_end = '2020-06-24';
usb_sessions(index).force_reprocess = true;
usb_sessions(index).ignore_datetime = {};

index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '200515 - 200527';
usb_sessions(index).date_start = '2020-05-12 00:00';
usb_sessions(index).date_start = '2020-05-18 09:30';
usb_sessions(index).date_end = '2020-05-28 00:00';
usb_sessions(index).force_reprocess = true;
usb_sessions(index).ignore_datetime = {'2020-05-18 10:00', '2020-05-18 10:30'};


index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '200320-200324';
usb_sessions(index).date_start = '2020-03-20 19:30';
usb_sessions(index).date_end = '2020-03-25 00:00';
usb_sessions(index).force_reprocess = false;
usb_sessions(index).ignore_datetime = {};

index = length(usb_sessions)+1;
% redoing session, same name different start date
usb_sessions(index).name = '200309-200310';
usb_sessions(index).date_start = '2020-03-09 18:30';
usb_sessions(index).date_end = '2020-03-10 19:00';
usb_sessions(index).force_reprocess = false;
usb_sessions(index).ignore_datetime = {};

% many sessions were deleted here due to a problem in hdd
% data can be "recovered" by looking at the filenames in the figures/
% folder

index = length(usb_sessions)+1;
usb_sessions(index).name = '200229-200303';
usb_sessions(index).date_start = '2020-02-29 06:30';
usb_sessions(index).date_end = '2020-03-03 18:00';
usb_sessions(index).force_reprocess = true;
usb_sessions(index).ignore_datetime = {};

index = length(usb_sessions)+1;
usb_sessions(index).name = '200221-';
usb_sessions(index).date_start = '2020-02-21 10:30';
usb_sessions(index).date_end = '2020-02-27 23:30';
usb_sessions(index).ignore_datetime = {'2020-02-21 15:00'};
% usb_sessions(index).rotating_session = false;
% usb_sessions(index).error_bars = false;


index = length(usb_sessions)+1;
usb_sessions(index).name = '220805-220815-especial-greaves';
usb_sessions(index).date_start = '2022-08-05 11:00';
usb_sessions(index).date_start = '2022-08-06 03:30';
usb_sessions(index).date_end = '2022-08-15 10:30';
usb_sessions(index).day_session = false;
usb_sessions(index).y_scale = false;
usb_sessions(index).ignore_datetime = {};
usb_sessions(index).makeVideo = false;
usb_sessions(index).force_reprocess = false;
usb_sessions(index).minpeakdistance = 60;
usb_sessions(index).smooth_num_points = 20;
usb_sessions(index).filterDiskSize = 10;
usb_sessions(index).rotating_session = false;
usb_sessions(index).saveTxtData = false;
usb_sessions(index).remove_drift = true;
usb_sessions(index).removeOutliers = false;
usb_sessions(index).error_bars = false;

index = length(usb_sessions)+1;
usb_sessions(index).name = '220706-220706-vidrio-vidrio-aire';
usb_sessions(index).date_start = '2022-07-04 17:00';
usb_sessions(index).date_end = '2022-07-06 10:00';
usb_sessions(index).day_session = false;
usb_sessions(index).y_scale = false;
usb_sessions(index).ignore_datetime = {};
usb_sessions(index).makeVideo = false;
usb_sessions(index).force_reprocess = true;
usb_sessions(index).minpeakdistance = 60;
usb_sessions(index).smooth_num_points = 20;
usb_sessions(index).filterDiskSize = 10;
usb_sessions(index).rotating_session = false;
usb_sessions(index).saveTxtData = false;
usb_sessions(index).remove_drift = true;
usb_sessions(index).removeOutliers = false;
usb_sessions(index).error_bars = false;

index = length(usb_sessions)+1;
usb_sessions(index).name = '190320-190325-vidrio-aire-reanalisis-220717';
usb_sessions(index).date_start = '2019-03-20 10:00';
usb_sessions(index).date_start = '2019-03-20 20:30';
usb_sessions(index).date_end = '2019-03-25 15:30';
usb_sessions(index).day_session = false;
usb_sessions(index).y_scale = false;
usb_sessions(index).ignore_datetime = {};
usb_sessions(index).makeVideo = false;
usb_sessions(index).force_reprocess = true;
usb_sessions(index).minpeakdistance = 60;
usb_sessions(index).smooth_num_points = 20;
usb_sessions(index).filterDiskSize = 10;
usb_sessions(index).rotating_session = false;
usb_sessions(index).saveTxtData = false;
usb_sessions(index).remove_drift = true;
usb_sessions(index).removeOutliers = false;
usb_sessions(index).error_bars = false;

index = length(usb_sessions)+1;
usb_sessions(index).name = '180914-180915-vidrio-aire';
usb_sessions(index).date_start = '2018-09-14 19:00';
% usb_sessions(index).date_start = '2018-09-14 21:00';
usb_sessions(index).date_end = '2018-09-15 19:00';
usb_sessions(index).day_session = false;
usb_sessions(index).y_scale = false;
usb_sessions(index).ignore_datetime = {};
usb_sessions(index).makeVideo = false;
usb_sessions(index).force_reprocess = false;
usb_sessions(index).minpeakdistance = 60;
usb_sessions(index).smooth_num_points = 20;
usb_sessions(index).filterDiskSize = 10;
usb_sessions(index).rotating_session = false;
usb_sessions(index).saveTxtData = false;
usb_sessions(index).remove_drift = true;
usb_sessions(index).removeOutliers = false;
usb_sessions(index).error_bars = false;


index = length(usb_sessions)+1;
usb_sessions(index).name = '2200702-2200704-aire-vidrio-vidrio';
usb_sessions(index).date_start = '2022-07-02 17:00';
usb_sessions(index).date_end = '2022-07-10 14:00';
usb_sessions(index).day_session = false;
usb_sessions(index).y_scale = false;
usb_sessions(index).ignore_datetime = {};
usb_sessions(index).makeVideo = false;
usb_sessions(index).force_reprocess = false;
usb_sessions(index).minpeakdistance = 60;
usb_sessions(index).smooth_num_points = 20;
usb_sessions(index).filterDiskSize = 10;
usb_sessions(index).rotating_session = false;
usb_sessions(index).saveTxtData = true;
usb_sessions(index).remove_drift = true;
usb_sessions(index).removeOutliers = false;

index = length(usb_sessions)+1;
usb_sessions(index).name = '220630-220702-aire-vidrio-vidrio';
usb_sessions(index).date_start = '2022-06-30 20:00';
usb_sessions(index).date_end = '2022-07-02 14:00';
usb_sessions(index).day_session = false;
usb_sessions(index).y_scale = false;
usb_sessions(index).ignore_datetime = {};
usb_sessions(index).makeVideo = false;
usb_sessions(index).force_reprocess = false;
usb_sessions(index).minpeakdistance = 60;
usb_sessions(index).smooth_num_points = 20;
usb_sessions(index).filterDiskSize = 10;
usb_sessions(index).rotating_session = false;
usb_sessions(index).saveTxtData = true;
usb_sessions(index).remove_drift = true;
usb_sessions(index).removeOutliers = false;

index = length(usb_sessions)+1;
usb_sessions(index).name = 'aire-aire-paralelo-20200515-20200517';
usb_sessions(index).date_start = '2020-05-15 18:30';
usb_sessions(index).date_end = '2020-05-17 09:29';
usb_sessions(index).day_session = false;
usb_sessions(index).y_scale = false;
usb_sessions(index).ignore_datetime = {};
usb_sessions(index).makeVideo = false;
usb_sessions(index).force_reprocess = false;
usb_sessions(index).minpeakdistance = 60;
usb_sessions(index).smooth_num_points = 20;
usb_sessions(index).filterDiskSize = 10;
usb_sessions(index).rotating_session = false;
usb_sessions(index).saveTxtData = true;
usb_sessions(index).remove_drift = true;
usb_sessions(index).removeOutliers = false;

index = length(usb_sessions)+1;
usb_sessions(index).name = '2022-06-22-vidrio-vidrio-nivelado';
usb_sessions(index).date_start = '2022-06-22 18:10';
usb_sessions(index).date_end = '2022-06-30';
usb_sessions(index).day_session = false;
usb_sessions(index).y_scale = false;
usb_sessions(index).ignore_datetime = {};
usb_sessions(index).makeVideo = false;
usb_sessions(index).force_reprocess = false;
usb_sessions(index).minpeakdistance = 60;
usb_sessions(index).smooth_num_points = 20;
usb_sessions(index).filterDiskSize = 10;
usb_sessions(index).rotating_session = false;
usb_sessions(index).saveTxtData = true;
usb_sessions(index).remove_drift = true;
usb_sessions(index).removeOutliers = false;

index = length(usb_sessions)+1;
usb_sessions(index).name = '2022-06-17 vidrio-vidrio-raw';
usb_sessions(index).date_start = '2022-06-17 11:00';
usb_sessions(index).date_start = '2022-06-18 00:30';
usb_sessions(index).date_start = '2022-06-19 23:30';
usb_sessions(index).date_end = '2022-06-22';
usb_sessions(index).day_session = false;
usb_sessions(index).y_scale = false;
usb_sessions(index).ignore_datetime = {'2022-06-19 23:30'};
usb_sessions(index).makeVideo = false;
usb_sessions(index).force_reprocess = false;
usb_sessions(index).minpeakdistance = 60;
usb_sessions(index).smooth_num_points = 20;
usb_sessions(index).filterDiskSize = 10;
usb_sessions(index).rotating_session = false;
usb_sessions(index).saveTxtData = true;
usb_sessions(index).remove_drift = true;
usb_sessions(index).removeOutliers = false;

index = length(usb_sessions)+1;
usb_sessions(index).name = '2022-06-17 vidrio-vidrio';
usb_sessions(index).date_start = '2022-06-17 11:00';
usb_sessions(index).date_start = '2022-06-18 00:30';
usb_sessions(index).date_start = '2022-06-19 16:00';
usb_sessions(index).date_end = '2022-06-20';
usb_sessions(index).day_session = false;
usb_sessions(index).y_scale = false;
usb_sessions(index).ignore_datetime = {};
usb_sessions(index).makeVideo = false;
usb_sessions(index).force_reprocess = false;
usb_sessions(index).minpeakdistance = 60;
usb_sessions(index).smooth_num_points = 20;
usb_sessions(index).filterDiskSize = 10;
usb_sessions(index).rotating_session = false;
usb_sessions(index).saveTxtData = true;
usb_sessions(index).remove_drift = true;
usb_sessions(index).removeOutliers = false;

index = length(usb_sessions)+1;
usb_sessions(index).name = '20200321-2030-greaves';
usb_sessions(index).date_start = '2020-03-21 20:30';
usb_sessions(index).date_end = '2020-03-21 20:30';
usb_sessions(index).day_session = false;
usb_sessions(index).y_scale = false;
usb_sessions(index).ignore_datetime = {};
usb_sessions(index).makeVideo = false;
usb_sessions(index).force_reprocess = false;
usb_sessions(index).minpeakdistance = 60;
usb_sessions(index).smooth_num_points = 20;
usb_sessions(index).filterDiskSize = 10;
usb_sessions(index).rotating_session = false;
usb_sessions(index).saveTxtData = true;
usb_sessions(index).remove_drift = true;
usb_sessions(index).removeOutliers = false;


index = length(usb_sessions)+1;
usb_sessions(index).name = '20180921-greaves-comparacion1';
usb_sessions(index).date_start = '2018-09-21 00:00';
usb_sessions(index).date_end = '2018-09-21 23:30';
usb_sessions(index).day_session = false;
usb_sessions(index).y_scale = false;
usb_sessions(index).ignore_datetime = {};
usb_sessions(index).makeVideo = false;
usb_sessions(index).force_reprocess = false;
usb_sessions(index).minpeakdistance = 60;
usb_sessions(index).smooth_num_points = 20;
usb_sessions(index).filterDiskSize = 10;
usb_sessions(index).rotating_session = false;
usb_sessions(index).saveTxtData = true;
usb_sessions(index).remove_drift = true;

index = length(usb_sessions)+1;
usb_sessions(index).name = '20180921-1730-greaves';
usb_sessions(index).date_start = '2018-09-21 17:30';
usb_sessions(index).date_end = '2018-09-21 17:30';
usb_sessions(index).day_session = false;
usb_sessions(index).y_scale = false;
usb_sessions(index).ignore_datetime = {};
usb_sessions(index).makeVideo = false;
usb_sessions(index).force_reprocess = false;
usb_sessions(index).minpeakdistance = 60;
usb_sessions(index).smooth_num_points = 20;
usb_sessions(index).filterDiskSize = 10;
usb_sessions(index).rotating_session = false;
usb_sessions(index).saveTxtData = true;
usb_sessions(index).remove_drift = true;

index = length(usb_sessions)+1;
usb_sessions(index).name = '200601-200625-con-deriva';
usb_sessions(index).date_start = '2020-06-01 17:30';
usb_sessions(index).date_start = '2020-06-09 13:00';
usb_sessions(index).date_end = '2020-06-25 03:00';
usb_sessions(index).ignore_datetime = {};
usb_sessions(index).force_reprocess = false;

index = length(usb_sessions)+1;
usb_sessions(index).name = '200515-200531-con-deriva';
usb_sessions(index).date_start = '2020-05-15';
usb_sessions(index).date_end = '2020-05-31 23:30';
usb_sessions(index).ignore_datetime = {'2020-05-18 10:00', '2020-05-26 20:00', ...
    '2020-05-26 20:30', '2020-05-26 21:00', '2020-05-26 22:00'};
usb_sessions(index).force_reprocess = false;

% % index = length(usb_sessions)+1;
% % usb_sessions(index).name = '180818-181216-con-deriva';
% % usb_sessions(index).date_start = '2018-08-18';
% % % usb_sessions(index).date_start = '2018-12-16 18:00';
% % usb_sessions(index).date_end = '2018-12-16 23:30';
% % usb_sessions(index).ignore_datetime = {...
% %     '2018-08-26 14:00', '2018-09-10 18:00','2018-09-14 21:00', ...
% %     '2018-08-21 18:30', '2018-08-21 19:00'};
%
% index = length(usb_sessions)+1;
% usb_sessions(index).name = '190910-190930-con-deriva';
% usb_sessions(index).date_start = '2019-09-10';
% usb_sessions(index).date_end = '2019-09-30 23:30';
% usb_sessions(index).day_session = false;
% usb_sessions(index).ignore_datetime = {'2019-09-22 13:30', '2019-09-22'};
%
% index = length(usb_sessions)+1;
% usb_sessions(index).name = '200810-200820-con-deriva';
% usb_sessions(index).date_start = '2020-08-10 13:30';
% usb_sessions(index).date_end = '2020-08-20 13:30';
% usb_sessions(index).ignore_datetime = {'2020-08-18 21:30'};
%
% index = length(usb_sessions)+1;
% usb_sessions(index).name = '200810-200820';
% usb_sessions(index).date_start = '2020-08-10 13:30';
% usb_sessions(index).date_end = '2020-08-20 13:30';
% usb_sessions(index).ignore_datetime = {'2020-08-18 21:30'};
%
% index = length(usb_sessions)+1;
% usb_sessions(index).name = '190802-190804';
% usb_sessions(index).date_start = '2019-08-02 11:00';
% usb_sessions(index).date_end = '2019-08-04 21:30';
%
% index = length(usb_sessions)+1;
% usb_sessions(index).name = '200917-200919';
% usb_sessions(index).date_start = '2020-09-17';
% usb_sessions(index).date_end = '2020-09-19 23:30';
% % usb_sessions(index).date_end = '2019-09-30 23:30';
% % usb_sessions(index).date_end = '2019-09-15 22:30';
% usb_sessions(index).day_session = false;
% usb_sessions(index).y_scale = false;
% usb_sessions(index).ignore_folder = {};
% usb_sessions(index).ignore_datetime = {'2019-09-22 13:30', '2019-09-22'};
% usb_sessions(index).makeVideo = false;
% usb_sessions(index).force_reprocess = false;
% usb_sessions(index).minpeakdistance = 20;
% usb_sessions(index).smooth_num_points = 20;
% usb_sessions(index).filterDiskSize = 10;
% usb_sessions(index).rotating_session = false;
%
% index = length(usb_sessions)+1;
% usb_sessions(index).name = '190910-190930';
% usb_sessions(index).date_start = '2019-09-10';
% usb_sessions(index).date_start = '2019-09-25 16:00';
% usb_sessions(index).date_end = '2019-09-30 23:30';
% % usb_sessions(index).date_end = '2019-09-15 22:30';
% usb_sessions(index).day_session = false;
% usb_sessions(index).y_scale = false;
% usb_sessions(index).ignore_folder = {};
% usb_sessions(index).ignore_datetime = {'2019-09-22 13:30', '2019-09-22'};
% usb_sessions(index).makeVideo = false;
% usb_sessions(index).force_reprocess = false;
% usb_sessions(index).minpeakdistance = 20;
% usb_sessions(index).smooth_num_points = 20;
% usb_sessions(index).filterDiskSize = 10;
% usb_sessions(index).rotating_session = false;
%
%
% index = length(usb_sessions)+1;
% usb_sessions(index).name = '180818-181216';
% usb_sessions(index).date_start = '2018-08-18';
% % usb_sessions(index).date_start = '2018-12-16 18:00';
% usb_sessions(index).date_end = '2018-12-16 23:30';
% usb_sessions(index).day_session = false;
% usb_sessions(index).y_scale = false;
% usb_sessions(index).ignore_datetime = {...
%     '2018-08-26 14:00', '2018-09-10 18:00','2018-09-14 21:00', ...
%     '2018-08-21 18:30', '2018-08-21 19:00'};
% usb_sessions(index).makeVideo = false;
% usb_sessions(index).force_reprocess = false;
% usb_sessions(index).minpeakdistance = 60;
% usb_sessions(index).smooth_num_points = 20;
% usb_sessions(index).filterDiskSize = 10;
%
%
% index = length(usb_sessions)+1;
% usb_sessions(index).name = '180818-181216-filtered';
% usb_sessions(index).date_start = '2018-08-18';
% % usb_sessions(index).date_start = '2018-12-16 18:00';
% usb_sessions(index).date_end = '2018-12-16 23:30';
% usb_sessions(index).day_session = false;
% usb_sessions(index).y_scale = false;
% usb_sessions(index).ignore_datetime = {...
%     '2018-08-26 14:00', '2018-09-10 18:00','2018-09-14 21:00', ...
%     '2018-08-21 18:30', '2018-08-21 19:00'};
% usb_sessions(index).makeVideo = false;
% usb_sessions(index).force_reprocess = false;
% usb_sessions(index).minpeakdistance = 60;
% usb_sessions(index).smooth_num_points = 20;
% usb_sessions(index).filterDiskSize = 10;
%
% index = length(usb_sessions)+1;
% usb_sessions(index).name = '180818-181216-filtered';
% usb_sessions(index).date_start = '2018-08-18';
% % usb_sessions(index).date_start = '2018-12-16 18:00';
% usb_sessions(index).date_end = '2018-12-16 23:30';
% usb_sessions(index).day_session = false;
% usb_sessions(index).y_scale = false;
% usb_sessions(index).ignore_datetime = {...
%     '2018-08-26 14:00', '2018-09-10 18:00','2018-09-14 21:00', ...
%     '2018-08-21 18:30', '2018-08-21 19:00'};
% usb_sessions(index).makeVideo = false;
% usb_sessions(index).force_reprocess = false;
% usb_sessions(index).minpeakdistance = 60;
% usb_sessions(index).smooth_num_points = 20;
% usb_sessions(index).filterDiskSize = 10;
% %%%%%%%%%%%%%%%%%%%
%
%
% index = length(usb_sessions)+1;
% usb_sessions(index).name = '20190901-20190922';
% usb_sessions(index).date_start = '2019-09-01';
% usb_sessions(index).date_start = '2019-09-22 12:00';
% usb_sessions(index).date_end = '2019-09-22 12:00';
% usb_sessions(index).day_session = false;
% usb_sessions(index).y_scale = false;
% usb_sessions(index).ignore_datetime = {'2019-09-22 13:30'};
% usb_sessions(index).ignore_folder = {};
% usb_sessions(index).makeVideo = false;
% usb_sessions(index).force_reprocess = false;
% usb_sessions(index).minpeakdistance = 20;
% usb_sessions(index).smooth_num_points = 20;
% usb_sessions(index).filterDiskSize = 10;
% usb_sessions(index).rotating_session = false;
%
% index = length(usb_sessions)+1;
% usb_sessions(index).name = '20190923-20190930';
% usb_sessions(index).date_start = '2019-09-23';
% usb_sessions(index).date_start = '2019-09-26 19:00';
% usb_sessions(index).date_end = '2019-09-30';
% usb_sessions(index).day_session = false;
% usb_sessions(index).y_scale = false;
% usb_sessions(index).ignore_datetime = {'2019-09-25 16:00', '2019-09-26 13:00'};
% usb_sessions(index).ignore_folder = {};
% usb_sessions(index).makeVideo = false;
% usb_sessions(index).force_reprocess = false;
% usb_sessions(index).minpeakdistance = 20;
% usb_sessions(index).smooth_num_points = 20;
% usb_sessions(index).filterDiskSize = 10;
% usb_sessions(index).rotating_session = false;
%
% index = length(usb_sessions)+1;
% usb_sessions(index).name = '20210426-20210430-MM';
% usb_sessions(index).date_start = '2021-04-29 08:00';
% usb_sessions(index).date_start = '2021-04-29 12:00';
% usb_sessions(index).date_end = '2021-04-30 10:30';
% usb_sessions(index).day_session = false;
% usb_sessions(index).y_scale = false;
% usb_sessions(index).ignore_datetime = {'2021-04-29 06:00', ...
%     '2021-04-29 08:00', '2021-04-29 12:00'};
% usb_sessions(index).makeVideo = false;
% usb_sessions(index).force_reprocess = false;
% usb_sessions(index).minpeakdistance = 20;
% usb_sessions(index).smooth_num_points = 20;
% usb_sessions(index).filterDiskSize = 10;
% usb_sessions(index).rotating_session = false;
%
% index = length(usb_sessions)+1;
% usb_sessions(index).name = '20210430-MM';
% usb_sessions(index).date_start = '2021-04-30 16:00';
%
% usb_sessions(index).date_start = '2021-05-01 15:30';
%
% usb_sessions(index).date_end = '2021-05-30 10:30';
% usb_sessions(index).day_session = false;
% usb_sessions(index).y_scale = false;
% usb_sessions(index).ignore_datetime = {'2021-05-01 05:30', '2021-05-01 15:30'};
% usb_sessions(index).makeVideo = false;
% usb_sessions(index).force_reprocess = false;
% usb_sessions(index).minpeakdistance = 50;
% usb_sessions(index).smooth_num_points = 20;
% usb_sessions(index).filterDiskSize = 10;
% usb_sessions(index).rotating_session = false;
% usb_sessions(index).ratio_fringe_separation = .75;
%
%
% index = length(usb_sessions)+1;
% usb_sessions(index).name = '20210501-MM-robert';
% usb_sessions(index).date_start = '2021-05-01 07:00';
% usb_sessions(index).date_end = '2021-05-01 08:00';
% usb_sessions(index).day_session = false;
% usb_sessions(index).y_scale = false;
% usb_sessions(index).ignore_datetime = {'2021-05-01 05:30'};
% usb_sessions(index).makeVideo = true;
% usb_sessions(index).force_reprocess = true;
% usb_sessions(index).minpeakdistance = 50;
% usb_sessions(index).smooth_num_points = 20;
% usb_sessions(index).filterDiskSize = 10;
% usb_sessions(index).rotating_session = false;
% usb_sessions(index).ratio_fringe_separation = .75;
%
%
% index = length(usb_sessions)+1;
% usb_sessions(index).name = '20210520-MM';
% usb_sessions(index).date_start = '2021-05-20 14:00';
% usb_sessions(index).date_end = '2021-06-01 08:00';
% usb_sessions(index).day_session = false;
% usb_sessions(index).y_scale = false;
% usb_sessions(index).ignore_datetime = {};
% usb_sessions(index).makeVideo = false;
% usb_sessions(index).force_reprocess = false;
% usb_sessions(index).minpeakdistance = 50;
% usb_sessions(index).smooth_num_points = 20;
% usb_sessions(index).filterDiskSize = 10;
% usb_sessions(index).rotating_session = false;
% usb_sessions(index).ratio_fringe_separation = .75;
%
% index = length(usb_sessions)+1;
% usb_sessions(index).name = '20210426-greaves';
% usb_sessions(index).date_start = '2021-04-26 17:30';
% usb_sessions(index).date_end = '2021-04-26 18:00';
% usb_sessions(index).day_session = false;
% usb_sessions(index).y_scale = false;
% usb_sessions(index).ignore_datetime = {};
% usb_sessions(index).makeVideo = false;
% usb_sessions(index).force_reprocess = false;
% usb_sessions(index).minpeakdistance = 50;
% usb_sessions(index).smooth_num_points = 20;
% usb_sessions(index).filterDiskSize = 10;
% usb_sessions(index).rotating_session = false;
% usb_sessions(index).ratio_fringe_separation = .70;
% usb_sessions(index).saveTxtData = true;
%
% index = length(usb_sessions)+1;
% usb_sessions(index).name = '20191101-20191124';
% usb_sessions(index).date_start = '2019-11-01 12:30';
% % usb_sessions(index).date_start = '2019-11-24 07:00';
% usb_sessions(index).date_end = '2019-11-24 08:30';
% usb_sessions(index).day_session = false;
% usb_sessions(index).y_scale = false;
% usb_sessions(index).ignore_datetime = {'2019-11-01 16:00','2019-11-01 16:30','2019-11-01 17:00' ...
%     '2019-11-01 17:30', '2019-11-02 04:30'};
% usb_sessions(index).makeVideo = false;
% usb_sessions(index).force_reprocess = false;
% usb_sessions(index).minpeakdistance = 20;
% usb_sessions(index).smooth_num_points = 20;
% usb_sessions(index).filterDiskSize = 10;
% usb_sessions(index).rotating_session = false;
