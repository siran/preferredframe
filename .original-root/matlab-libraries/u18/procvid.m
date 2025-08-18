% clc
clear all

vid = VideoReader('C:\Users\AMR\Desktop\video1.avi');
vidFrames = vid.NumberOfFrames;
vidHeight = vid.Height;
vidWidth = vid.Width;

% hpeaks1.release();
hpeaks1 = dsp.PeakFinder;
hpeaks1.PeakIndicesOutputPort = true;
hpeaks1.PeakValuesOutputPort = true;
hpeaks1.MaximumPeakCount = 20;
hpeaks1.PeakType = 'Maxima';

hpeaks1.IgnoreSmallPeaks = true;

tic
tframes = 50000;
pts = nan(tframes, 20);
for f = 2 : tframes %vidFrames
%     if (mod(k, 15) ~= 0)
%         continue
%     end
    if (mod(f, 1000) == 0) 
        elap = toc;
        rem = toc*tframes/f - elap;
        fprintf('frames proc.: %5.3f%% (%d/%d) elap.: %5.0fs rem.: %6.2f h (%6.2f m, %6.2f s) \n', f/tframes*100, f, tframes, toc, rem/60/60, rem/60, rem);
    end
    vidFrame = read(vid, f);
    vidFrameCol = smooth(double(vidFrame(:,1,1)), 20);
    
    [cnt1, idx1, val1] = step(hpeaks1, vidFrameCol);

     pts(f,:) = int32(idx1);   
%     hold on
%     plot(idx1,val1,'X');  
%     plot(vidFrameCol,'-');
end

% plot(pts,'.')
hpeaks1.release();
% data = adjustdata(pts);