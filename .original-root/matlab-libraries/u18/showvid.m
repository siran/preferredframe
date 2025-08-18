function showvid( xyloObj, finit, fend )
%showvid( vid, finit, fend )
%   xyloObj: as in xyloObj = VideoReader('C:\Users\AMR\Desktop\video1.avi')
%      also can be the path to video
% finit: initial frame
% fend: final frame

if isstr(xyloObj)
    xyloObj = VideoReader(vid);
end

nFrames = xyloObj.NumberOfFrames;
vidHeight = xyloObj.Height;
vidWidth = xyloObj.Width;

% Preallocate movie structure.
mov(1:fend-finit) = ...
    struct('cdata', zeros(vidHeight, vidWidth, 3, 'uint8'),...
           'colormap', []);

% Read one frame at a time.
for k = 1:(fend-finit)
    mov(k).cdata = read(xyloObj, k+finit);
end

% Size a figure based on the video's width and height.
hf = figure;
set(hf, 'position', [150 150 vidWidth vidHeight])

% Play back the movie once at the video's frame rate.
movie(hf, mov, 1, xyloObj.FrameRate);

end

