function varargout = sineFitDemo(varargin)
%sineFitDemo
%Demo GUI for fitting noisy sine curves.
%Explanation
%   Input: all values are floating point, except 'num samples' must be integer!
%      'Number of periods' influences x end.
%         The number of periods may be less than 1, tested down to 0.1 periods.
%      'Samples per period' must be larger than 2.0. Interacts autom. with 'num samples'.
%      'Num samples' must be integer! Interacts autom. with 'Samples per period'
%          Minimum 4 samples in order to detect parameters.
%      'signal to noise': Noise is applied on the sine curve excluding offset
%         and is in dB.
%   Output: Estimate of the noise free sine curve parameters.
%   Best regression: The parameters of the clean sine are used as intial data for fminsearch.m.
%      If the result is different to the clean parameters, another sine fits the noisy sine better.
%   FFT: Parameters at the peak of the FFT. Offs. is in general the mean value of the input.
%   Process time: Time used by sineFit.m.
%   Run: Calculate the output for the input values.
%   Other noise: Run same clean sine with same SNR, but different random noise added.
%   Run xy.mat: runs your y(x), this must be in a 'xy.mat' file like:
%      x=[1,2,3,...]
%      y=[1,2,1,...]
%      Optional, if you know the noise free parameters add this variable:
%           paramsClean=[1,2,3,4];%[offset,amp,f,phase]
%           if you know in addition SNR:
%           paramsClean=[1,2,3,4,33];%[offset,amp,f,phase,SNR]
%           SNR is only for information.
%      see example file 'xy.mat'.
%    'Save as xy.mat': Save the input and output data to xy.mat.
%       x and y values of noisy input
%       paramsClean: Parameters of noise free sine:
%           [offset, amplitude, frequency, phase, SNR]
%       SineParamsOut: Estimated parameters of noisy sine:
%           [offset, amplitude, frequency, phase, MSE]
%       SineParamsOut is also present in the workspace.
%Definition of >10% deviation, red:
%	 The amplitude or the frequency is marked red,
%   if the deviation is more than 10% compared to the noise free original sine.
%	 The offset can be zero and is considered to be very different to the original sine,
%   if it deviates by more than 10% of the original offset
%   and more than 10% of the original amplitude.
%	 The phase is marked red if it deviates by more than 10% of 2pi.
%Definition of <10% deviation, orange:
%  Like above, the deviation is between 1% and 10%.
%Definition of <1% deviation, green:
%  Like above, the deviation is less than 1%.

% Last Modified by GUIDE v2.5 01-Nov-2020 10:40:47
%Author: Peter Seibold

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
  'gui_Singleton',  gui_Singleton, ...
  'gui_OpeningFcn', @sineFitDemo_OpeningFcn, ...
  'gui_OutputFcn',  @sineFitDemo_OutputFcn, ...
  'gui_LayoutFcn',  [] , ...
  'gui_Callback',   []);
if nargin && ischar(varargin{1})
  gui_State.gui_Callback = str2func(varargin{1});
end
if nargout
  [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
  gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT

% --- Executes just before sineFitDemo is made visible.
function sineFitDemo_OpeningFcn(hObject, eventdata, handles, varargin)
movegui(hObject,'west') 
handles.output = hObject;
%Smiley:
imSmiley=handles.axSmiley.UserData;
axes(handles.axSmiley);
handles.Smiley=imshow(imSmiley);%for some reason it deletes tag and userdata of axSmiley
set(handles.axSmiley,'Tag','axSmiley','UserData',imSmiley);%Restore values
set(handles.Smiley,'Visible','off');
guidata(hObject, handles);% Update handles structure
CreateDrawSin(0,handles);
cmdRun_Callback(hObject, eventdata, handles);

% --- Outputs from this function are returned to the command line.
function varargout = sineFitDemo_OutputFcn(hObject, eventdata, handles)
varargout{1} = handles.output;

function editoffset_Callback(hObject, eventdata, handles)
CreateDrawSin(1,handles);

function editAmplitude_Callback(hObject, eventdata, handles)
CreateDrawSin(2,handles);

function editf_Callback(hObject, eventdata, handles)
CreateDrawSin(3,handles);

function editPhaseshift_Callback(hObject, eventdata, handles)
CreateDrawSin(4,handles);

function txtNumPeriods_Callback(hObject, eventdata, handles)
CreateDrawSin(5,handles);

function editsamplesperperiod_Callback(hObject, eventdata, handles)
CreateDrawSin(6,handles);

function editNumSamples_Callback(hObject, eventdata, handles)
CreateDrawSin(7,handles);

function editNoise_Callback(hObject, eventdata, handles)
CreateDrawSin(8,handles);

function edittstart_Callback(hObject, eventdata, handles)
CreateDrawSin(9,handles);

% --- Executes on button press in cmdRun.
function cmdRun_Callback(hObject, eventdata, handles)
global x y paramsClean SineParamsOut FFTparamsOut paramsBest
%  FillEditBoxesInput(handles)
tic;
  SineParamsOut=sineFit(x,y,handles.chkGraphics.Value);
set(handles.txtProcessTime,'string',[sprintf('%0.0f',toc*1000) ' ms']);
MSEout=SineParamsOut(5);
%plot sine
x2=x(1):min(0.002*(x(end)-x(1)),(x(2)-x(1))/10):x(end);
y2=SineParamsOut(1)+SineParamsOut(2)*sin(2*pi*SineParamsOut(3)*x2+SineParamsOut(4));%result
axes(handles.plotFig);
pN(1)=plot(x,y,'Color',[0.8,0,0]);%input
hold on;
plot(x,y,'k.');%input dot
pN(2)=plot(x2,y2,'b-');%result
xlabel('Time [s]')
extra=(x2(end)-x2(1))*0.03;
xlim([x2(1)-extra x2(end)+extra]);
grid on;
paramsBest=[[] [] [] [] []];
if length(paramsClean)>3
  xstart=x(1);
  xend=x(end);
  extra=(xend-xstart)*0.02;
  xClean=xstart-extra:min(0.002*(xend-xstart),(x(2)-x(1))/10):xend+extra;
  yClean=paramsClean(1)+paramsClean(2)*sin(2*pi*paramsClean(3)*xClean+paramsClean(4));
  pN(3)=plot(xClean,yClean,'g-');%plot clean sine
  uistack(pN(2),'top');%put result line on top
  legend([pN(1),pN(3),pN(2)],'input','original','output','Location','best');
  %best regression: use input values of GUI for regression
  initial_params=paramsClean(1:4);
  fun = @(SineParams)sseval(SineParams,x,y);
  paramsBest = fminsearch(fun,initial_params,...
    optimset('MaxFunEvals',200000,'MaxIter',200000));
  MSEb=(sum((y - (paramsBest(1)+paramsBest(2)*sin(2*pi*paramsBest(3)*x+paramsBest(4)))).^2))/numel(x);
  paramsBest(4)=rem(paramsBest(4),2*pi);
  if paramsBest(4)<0;paramsBest(4)=paramsBest(4)+2*pi; end;
  paramsBest(5)=MSEb;
else
  legend([pN(1),pN(2)],'input','output','Location','best');
end
hold off;
assignin('base', 'SineParamsOut', SineParamsOut);%Result in workspace, you may delete this statement
PlotFFT(handles);
MSEfft=(sum((y - (FFTparamsOut(1)+FFTparamsOut(2)*...
  sin(2*pi*FFTparamsOut(3)*x+FFTparamsOut(4)))).^2))/numel(x);
FFTparamsOut(5)= MSEfft;
FillEditBoxesInput(handles)
TxtBoxesErrorColor(handles);
%Message
if  isequal(SineParamsOut(1:4),FFTparamsOut(1:4))
  set(handles.txtMessage2,'String','Output parameters are FFT parameters');
elseif length(paramsClean)>3 && MSEb*1.0001+1e-7<MSEout
  set(handles.txtMessage2,'String','Output regression not optimal, MSE could be better.');
else
  set(handles.txtMessage2,'String','');
end

% --- Executes on button press in cmdOtherNoise.
function cmdOtherNoise_Callback(hObject, eventdata, handles)
global paramsClean
if length(paramsClean)<5
  set(handles.txtMessage,'String',...
    'ERROR: Not enough parameters of input sine!',...
    'Foregroundcolor',[.8 0 0]);
  return;
end
CreateDrawSin(0,handles);
cmdRun_Callback(hObject, eventdata, handles);

function cmdRunMyXY_Callback(hObject, eventdata, handles)
global x y paramsClean
TxtOutClear(handles);
set(handles.txtMessage,'String','');
%check if file exists
if exist(fullfile(pwd, 'xy.mat'), 'file')==2
  paramsClean=NaN;%overwritten if existing in 'xy.mat'
  load(fullfile(pwd, 'xy.mat'));
  cmdRun_Callback(hObject, eventdata, handles);
else
  set(handles.txtMessage,'String',...
    'ERROR: xy.mat not found in current directory!',...
    'Foregroundcolor',[.8 0 0]);
end

% --- Executes on button press in cmdSaveInOut.
function cmdSaveInOut_Callback(hObject, eventdata, handles)
global x y paramsClean SineParamsOut
save('xy.mat','x','y', 'paramsClean', 'SineParamsOut');

function cmdHelp_Callback(hObject, eventdata, handles)
help sineFitDemo;

function CreateDrawSin(Flag,handles)
%runs if input values (offset, amplitude, etc.) changed by user or with cmdRun
global x y paramsClean
TxtOutClear(handles);%Clear output numbers
set(handles.txtMessage,'String','');%Clear message box
cla(handles.plotFigFFT,'reset');%Clear FFT plot
offset=str2double(get(handles.editoffset,'string'));
amplitude=str2double(get(handles.editAmplitude,'string'));
f=str2double(get(handles.editf,'string'));
Phi0=str2double(get(handles.editPhaseshift,'string'));
numPeriods=str2double(get(handles.txtNumPeriods,'string'));
samplesPperiod=str2double(get(handles.editsamplesperperiod,'string'));
numSamples=str2double(get(handles.editNumSamples,'string'));
NoiseLevelStr=get(handles.editNoise,'string');
if numel(NoiseLevelStr)>2 && strcmp(NoiseLevelStr(1:2),'~ ') 
  set(handles.editNoise,'string',NoiseLevelStr(3:end));
end
NoiseLevel=str2double(get(handles.editNoise,'string'));
xstart=str2double(get(handles.edittstart,'string'));
%adjust samplesPperiod, NumSamples accordingly:
if Flag==5  && sum(isnan([numPeriods,samplesPperiod]))==0
  %Num periods changed by user
  %Keep samples per period if num periods >1, else keep num samples
  if numPeriods>=1
    numSamples=max([round(numPeriods*samplesPperiod),...
      ceil(2*numPeriods+eps(2*numPeriods)),4]);
  end
elseif Flag==6 && sum(isnan([numPeriods,samplesPperiod]))==0
  %Samples per period changed by user
  numSamples=max(round(numPeriods*samplesPperiod),3);
elseif Flag==7 && ~isnan(numSamples)
  %Num samples changed by user
  %numSamples must be an integer number!
  numSamples=max(round(numSamples),3);
end
if numSamples<=2*numPeriods || numSamples<4
  Ns=max(ceil(2*numPeriods+eps(2*numPeriods)),4);
  set(handles.txtMessage,'String',...
    ['WARNING: Not enough samples to detect parameters, num samples >= ' num2str(Ns)],...
    'Foregroundcolor',[.7 .4 0]);
end

samplesPperiod=numSamples/numPeriods;
set(handles.editsamplesperperiod,'String',num2str(samplesPperiod,6));
set(handles.editNumSamples,'String',num2str(numSamples));
%check if inputs are numbers:
if sum(isnan([offset,amplitude,f,Phi0,numPeriods,samplesPperiod,numSamples,NoiseLevel,xstart]))>0
  cla(handles.plotFig,'reset');%clear sine plot
  set(handles.txtMessage,'String',...
    'Please insert numbers as input!',...
    'Foregroundcolor',[.8 0 0]);
  return
end
%create sine acc. to user input
xend=xstart+numPeriods/f;
x=xstart:1/(f*samplesPperiod):xend;
x=x(1:end-1);
xend=x(end);
paramsClean=[offset,amplitude,f,Phi0,NoiseLevel];
set(handles.edittend,'string',num2str(xend,4));
set(handles.editNumSamples,'string',num2str(length(x),4));
ysin=amplitude*sin(2*pi*f*x+Phi0);
if NoiseLevel<99 % no noise if SNR>=99
  if exist('awgn.m','file')==2
    %communication_toolbox necessary
    ysin=awgn(ysin,NoiseLevel,'measured');
  else
    %No Toolbox necessary
    ysin=ysin+.7071*amplitude*randn(size(ysin))/(10^(NoiseLevel/20));
  end
end
y=offset+ysin;
MSEin=(sum((y - (offset+amplitude*sin(2*pi*f*x+Phi0))).^2))/numel(x);
set(handles.txtMSEin,'String',num2str(MSEin,4));
%plot created sine
extra=(xend-xstart)*0.02;% for longer green line
xClean=xstart-extra:min(0.002*(xend-xstart),(x(2)-x(1))/10):xend+extra;
yClean=offset+amplitude*sin(2*pi*f*xClean+Phi0);
axes(handles.plotFig);
pN=plot(x,y,'k.',xClean,yClean,'g-');%dot input, clean sine
hold on;
pN(3)=plot(x,y,'Color',[0.8,0,0]);% line input
legend([pN(3),pN(2)],'input','original','Location','best');
hold off;
xlabel('Time [s]')
extra=(xend-xstart)*0.01;
xlim([xClean(1)-extra xClean(end)+extra]);
grid on;

function PlotFFT(handles)
global x y paramsClean SineParamsOut FFTparamsOut
numSamples=length(x);
Ts=x(2)-x(1);%sampling Period
offs=mean(y);%DC value
y_m=y-offs;
n = 128*2^nextpow2(numSamples);%heavy zero padding
Y = fft(y_m,n);%Y(f)
n2=n/2;
P2 = abs(Y/numSamples);
P1 = P2(1:n2+1);
P1(2:end-1) = 2*P1(2:end-1);
fs = (0:n2)/n/Ts;% f scale
[maxFFT,maxFFTindx]=max(P1);
fPeak=fs(maxFFTindx);% f at peak
%Phase
Phip=angle(Y(maxFFTindx))+pi/2;%sin(90°+alpha)=cos(betta), alpha=-betta
%phase not correct due to rectangular window effect. OK for more than 1 period
Phip=Phip-x(1)*fPeak*2*pi;%shift for phi at x=0
Phip=rem(Phip,2*pi);
if Phip<0
  Phip=Phip+2*pi;
end
if numel(x)<12 || x(end)-x(1)<5/fPeak
  %Low sample number or low period number
  offs=(max(y)+min(y))/2;%Better results with offset by peak
elseif abs(offs)<0.1 && maxFFT>0.9
  offs=0;%Priority to 0
end
FFTparamsOut=[offs maxFFT fPeak Phip 0];
%plot FFT
axes(handles.plotFigFFT);
pFFTin=plot(fs,P1,'r-');
xlabel('Frequency [Hz]');
ylabel('Amplitude')
hold on;
pFFTmax=plot(fs(maxFFTindx),maxFFT,'r+','MarkerSize',12);
pFFTresult=plot(SineParamsOut(3),SineParamsOut(2),'b+','LineWidth',2,'MarkerSize',8);
plot([SineParamsOut(3),SineParamsOut(3)],[0,max(max(P1)*1.01,SineParamsOut(2))],'b-');
if length(paramsClean)>3
  %paramsClean present
  pFFTexp=plot(paramsClean(3),paramsClean(2),'gx','LineWidth',2);
  plot([paramsClean(3),paramsClean(3)],[0,max(maxFFT*1.01,paramsClean(2)*1.01)],'g-');
  hLeg=legend([pFFTin,pFFTexp,pFFTresult,pFFTmax],'Input FFT',...
    ['original:  ' num2str(paramsClean(2),3) ' | ' num2str(paramsClean(3),3) ' Hz'],...
    ['Result:     ' num2str(SineParamsOut(2),3) ' | ' num2str(SineParamsOut(3),3) ' Hz'],...
    ['max FFT:  ' num2str(maxFFT,3) ' | ' num2str(fs(maxFFTindx),3) ' Hz'],...
    'Location','best');
else
  hLeg=legend([pFFTin,pFFTresult,pFFTmax],'Input',...
    ['Result:       ' num2str(SineParamsOut(2),3) ' | ' num2str(SineParamsOut(3),3) ' Hz'],...
    ['max FFT:  ' num2str(maxFFT,3) ' | ' num2str(fs(maxFFTindx),3) ' Hz'],...
    'Location','best');
end
title(hLeg,'        amplitude | frequency','FontSize',8);
hold off;
grid on;

function FillEditBoxesInput(handles)
global x  paramsClean
if length(paramsClean)>3
  set(handles.editoffset,'string',num2str(paramsClean(1),4));
  set(handles.editAmplitude,'string',num2str(paramsClean(2),4));
  set(handles.editf,'string',num2str(paramsClean(3),4));
  set(handles.editPhaseshift,'string',num2str(paramsClean(4),4));
  numPeriods=(x(end)-x(1)+x(2)-x(1))*paramsClean(3);
  samplesperperiod=(length(x))/numPeriods;
  set(handles.txtNumPeriods,'string',num2str(numPeriods,6));
  set(handles.editsamplesperperiod,'string',num2str(samplesperperiod,6));
  if length(x)<=2*numPeriods || length(x)<4
    Ns=max(ceil(2*numPeriods+eps(2*numPeriods)),4);
    set(handles.txtMessage,'String',...
      ['WARNING: Not enough samples to detect parameters, num samples >= ' num2str(Ns)],...
      'Foregroundcolor',[.7 .4 0]);
  end
else
  set(handles.editoffset,'string','');
  set(handles.editAmplitude,'string','');
  set(handles.editf,'string','');
  set(handles.editPhaseshift,'string','');
  set(handles.txtNumPeriods,'string','');
  set(handles.editsamplesperperiod,'string','');
end
set(handles.editNumSamples,'string',num2str(length(x)));
set(handles.edittstart,'string',num2str(x(1),4));
set(handles.edittend,'string',num2str(x(end),4));
if length(paramsClean)==5
  set(handles.editNoise,'string',num2str(paramsClean(5),3));
else
  set(handles.editNoise,'string','');
end

function TxtOutClear(handles)
hTxt={handles.txtOffset,handles.txtAmplitude,handles.txtf,handles.txtPhi0,handles.txtMSEout;...%sine
  handles.txtFFToffs,handles.txtFFTamp,handles.txtFFTf,handles.txtFFTphi,handles.txtMSEfft;...%FFT
  handles.txtBestOffs,handles.txtBestAmp,handles.txtBestf,handles.txtBestPhi,handles.txtMSEb};%best regression
 Colors=[[1 1 1];[0.94 0.94 0.94];[0.94 0.94 0.94]];
for i=1:3
  for j=1:4
    set(hTxt{i,j},'BackgroundColor',Colors(i,:),'string',' ');
  end 
  set(hTxt{i,5},'string',' ');
end

function TxtBoxesErrorColor(handles)
global x y paramsClean SineParamsOut FFTparamsOut paramsBest
countGreen=0;%Display smiley if equal 4
hTxt={handles.txtOffset,handles.txtAmplitude,handles.txtf,handles.txtPhi0,handles.txtMSEout;...%sine output
  handles.txtFFToffs,handles.txtFFTamp,handles.txtFFTf,handles.txtFFTphi,handles.txtMSEfft;...%FFT
  handles.txtBestOffs,handles.txtBestAmp,handles.txtBestf,handles.txtBestPhi,handles.txtMSEb};%best regression
Pout=[SineParamsOut;FFTparamsOut;paramsBest];
%Display values of output
for i=1:2+(length(paramsClean)>3)%only outputs if paramsClean unknown
  for j=1:5
    set(hTxt{i,j,1},'string',num2str(Pout(i,j),4));
  end
end
%Error colors
if length(paramsClean)>3
  ErrorL1 = 0.01; % 1% error
  ErrorL10 = 0.1; % 10% error
  errorPi1 =2*pi*0.01; % 1% phase error
  errorPi10 = errorPi1*10; % 10% phase error
  green=[.9 1 .9];
  orange=[1 .95 .8];
  red=[1 .8 .8];
  OffClean=paramsClean(1);
  AmpClean=paramsClean(2);
  fClean=paramsClean(3);
  PhiClean=paramsClean(4);
 for i=1:3
  OffOut=Pout(i,1);
  AmpOut=Pout(i,2);
  fOut=Pout(i,3);
  PhiOut=Pout(i,4); 
    %Offset
   if abs(OffOut - OffClean) < ErrorL1 * AmpClean || abs(OffOut - OffClean) < ErrorL1 * abs(OffClean)
    set(hTxt{i,1},'BackgroundColor',green);
    if i==1;countGreen=countGreen+1;end
  elseif abs(OffOut - OffClean) < ErrorL10 * AmpClean || abs(OffOut - OffClean) < ErrorL10 * abs(OffClean)
    set(hTxt{i,1},'BackgroundColor',orange);
  else
    set(hTxt{i,1},'BackgroundColor',red);
  end
  %Amplitude
  if abs(AmpOut / AmpClean - 1) < ErrorL1
    set(hTxt{i,2},'BackgroundColor',green);
    if i==1;countGreen=countGreen+1;end
  elseif  abs(AmpOut / AmpClean - 1) < ErrorL10
    set(hTxt{i,2},'BackgroundColor',orange);
  else
    set(hTxt{i,2},'BackgroundColor',red);
  end
  %Frequency
  if abs(fOut / fClean - 1) < ErrorL1
    set(hTxt{i,3},'BackgroundColor',green);
    if i==1;countGreen=countGreen+1;end
  elseif abs(fOut / fClean - 1) < ErrorL10
    set(hTxt{i,3},'BackgroundColor',orange);
  else
    set(hTxt{i,3},'BackgroundColor',red);
  end
  %Phase
  if PhiOut < 1 && PhiClean > 5
    PhiOut = PhiOut + 2 * pi;
  elseif PhiOut > 5 && PhiClean < 1
    PhiOut = PhiOut - 2 * pi;
  end
  if abs(PhiOut - PhiClean) < errorPi1
    set(hTxt{i,4},'BackgroundColor',green);
    if i==1;countGreen=countGreen+1;end
  elseif abs(PhiOut - PhiClean) < errorPi10
    set(hTxt{i,4},'BackgroundColor',orange);
  else
    set(hTxt{i,4},'BackgroundColor',red);
  end
 end
 MSEin=(sum((y - (OffClean+AmpClean*sin(2*pi*fClean*x+PhiClean))).^2))/numel(x);
 set(handles.txtMSEin,'String',num2str(MSEin,4));
 set([handles.txtSNRtitle; handles.editNoise], 'TooltipString',...
['No noise added if SNR>=99.' char(10) 'SNR only on sine without offset.']);
else
 set(handles.txtMSEin,'String',''); 
 SNRe=10*log10(SineParamsOut(2)^2/abs(SineParamsOut(5))*0.5);%Estimated SNR by MSEout
 set(handles.editNoise,'string',['~ ' num2str(SNRe,1)]);
 set([handles.txtSNRtitle; handles.editNoise], 'TooltipString',...
['Rough estimate of SNR by MSE.' char(10) 'SNR only on sine without offset.']);
end
 if countGreen==4
   set(handles.Smiley,'Visible','on');
 else
   set(handles.Smiley,'Visible','off');
 end

% --- Executes when SineFitDemoFig is resized.
function SineFitDemoFig_SizeChangedFcn(hObject, eventdata, handles)
FigPos=get(handles.SineFitDemoFig,'Position');
set(handles.uipanel,'Position',[1 FigPos(4)-131 FigPos(3)-1 131]);

function sse = sseval(SineParams,x,y)
offs = SineParams(1);
A =SineParams(2);
f=SineParams(3);
Phi=SineParams(4);
sse = sum((y - (offs+A*sin(2*pi*f*x+Phi))).^2);


