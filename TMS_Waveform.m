function TMS_Waveform()
%% Generate TMS pulse trains and write them in a file to be used in the
% NEURON simulation.

% Receive TMS parameters
TMS_type = menu('Choose TMS pulse type:','Provided Monophasic Pulse','Generate Custom Monophasic Pulse','Provided Biphasic Pulse','Generate Custom Biphasic Pulse','Generate Custom Rectangular Pulse','Generate Custom Boost Pulse','Load Pulse from File');
STEP_type = menu('Choose step time (us) :','5','25 (Default)');

%%
prompt = {'\bfEnter the inter-pulse interval in ms:',...
    '\bf Enter the number of pulses:'};

dlgtitle = 'TMS Parameters';
dims = [1 92];
opts.Interpreter = 'tex';
opts.WindowStyle = 'normal';
definput = {'500','1'};
while 1
    answer = inputdlg(prompt,dlgtitle,dims,definput,opts);
    ipi = str2double(answer{1}); % inter-pulse interval
    nump = str2double(answer{2}); % number of pulses
    if ~isnan(ipi) && ~isnan(nump) && ipi>0 && nump>=1
        break
    end
    definput = answer;
    if isnan(ipi)
        definput{1} = 'Wrong format!';
    elseif ipi<=0
        definput{1} = 'Value should be positive!';
    end
    if isnan(nump)
        definput{2} = 'Wrong format!';
    elseif nump < 1
        definput{2} = 'At least one pulse is needed!';
    end
end

if TMS_type ~= 1 && TMS_type ~= 3 && TMS_type ~= 7  %If it's a custom pulse we need more input!
    prompt = {'\bfEnter the desired pulse width:',...
    '\bf Currently Unused! Leave as 1:'};
    dlgtitle = 'Custom Pulse Parameters';
    dims = [1 92];
    opts.Interpreter = 'tex';
    opts.WindowStyle = 'normal';
    definput = {'0.15','1'};
    
    while 1
        answer2 = inputdlg(prompt,dlgtitle,dims,definput,opts);
        desiredPulseWidth = str2double(answer2{1});
        mysteryVar = str2double(answer2{2}); 
        if ~isnan(ipi) && ~isnan(nump) && ipi>0 && nump>=1
            break
        end
        definput = answer2;
        if isnan(desiredPulseWidth)
            definput{1} = 'Wrong format!';
        elseif desiredPulseWidth<0.025
            definput{1} = 'Pulse width must be greater than 0.025!';
        elseif desiredPulseWidth>0.5
            definput{1} = 'Pulse width must be less than 0.5!';
        end
        if isnan(mysteryVar)
            definput{2} = 'Wrong format!';
        elseif mysteryVar < 1
            definput{2} = 'At least one pulse is needed!';
        end
    end
end
%% Read TMS single pulse file
dt = 0.005;
if TMS_type == 1
    load(['./original_waveforms' filesep 'TMS_mono.mat']);
elseif TMS_type == 2 %Generate a monophasic pulse!
    desiredPulseLength = desiredPulseWidth/0.1;
    scalingFactor = 360*0.005/desiredPulseLength;

    monoCurrent = zeros(round(360/scalingFactor),1);
    firstBound = round(50/scalingFactor);

    for i=1:firstBound
        monoCurrent(i) = 50*sin(2*pi*scalingFactor*i/200);
    end

    for i=firstBound+1:length(monoCurrent)
        monoCurrent(i) = monoCurrent(firstBound)*exp(-((scalingFactor*i)-50)/150);
    end

    TMS_E = diff(monoCurrent);
    TMS_E = [zeros(1,1); TMS_E; zeros(1,1)];
    TMS_E = TMS_E/max(TMS_E); %normalizing results

    TMS_t = (0:dt:(length(TMS_E)*dt)-dt)';
elseif TMS_type == 3
    load(['./original_waveforms' filesep 'TMS_bi.mat']);
elseif TMS_type == 4 %Generate a biphasic pulse!
    pulseFrequency = 1/desiredPulseWidth/2;
    TMS_t = (0:dt:(desiredPulseWidth+dt)*2)';
    TMS_E = cos(2*pi*pulseFrequency*(TMS_t-dt));
    TMS_E(1) = 0;
    TMS_E(end) = 0;
elseif TMS_type == 5 %Generate a rectangular pulse!
    totalTime = 0.3; %Could also request totalTime from user to have a truely variable pulse!

    TMS_E = zeros(totalTime/dt+1,1);
    recoveryIntensity = -desiredPulseWidth/(totalTime - desiredPulseWidth);

    TMS_E(1:(desiredPulseWidth/dt+1)) = 1;
    TMS_E((desiredPulseWidth/dt+2):end) = recoveryIntensity;
    TMS_E = [zeros(1,1); TMS_E; zeros(5,1)];
    TMS_t =(0:dt:length(TMS_E)*dt-dt)';
elseif TMS_type == 6 %Generate a boost pulse!
    %currently have 1.8 ms of pulse
    %Pulse width is 0.8 natively

    desiredPulseLength = desiredPulseWidth/0.8;
    scalingFactor = round(360*0.005/desiredPulseLength);

    boostCurrent = zeros(round(360/scalingFactor),1);

    firstBound = round((160/360)*length(boostCurrent));
    secondBound = round((200/360)*length(boostCurrent));
    thirdBound = length(boostCurrent);

    for i=1:firstBound
        boostCurrent(i)=sin(scalingFactor*(pi/2*(i)/160));
    end
    for i=firstBound+1:secondBound
        boostCurrent(i)=cos(pi*((scalingFactor*i)-160)/40); 
    end   
    for i=secondBound+1:thirdBound
        boostCurrent(i)=-sin(pi/2+pi/2*((scalingFactor*i)-200)/160);
    end

    for i= secondBound+1:thirdBound
        if boostCurrent(i) > 0
            boostCurrent(i) = 0;
        end 
    end

    TMS_E = diff(boostCurrent);
    TMS_E = -TMS_E./min(TMS_E);    %Normalizing result

    TMS_t = (0:dt:(length(TMS_E)*dt)-dt)';
elseif TMS_type == 7 %Request user file
    [fileName, pathName] = uigetfile('.mat');
    load([pathName filesep fileName]);
end

%% Generate pulse train
step = 0.005;
if length(TMS_E) > round(ipi/dt)
    error('Inter-pulse interval cannot be shorter than TMS pulse duration.');
end
delay_start = 40; % delay at the beginning before TMS delivery 40
delay_end = 40; % delay after the TMS delivery 40
ipi = round(ipi/dt)*dt;
train_length = delay_start + (nump-1)*ipi + delay_end; % in ms
train_t = (0:dt:train_length)';  %creates the sample numbers

pulse_extend = [TMS_E; zeros(round(ipi/dt)-length(TMS_E),1)];

train_E = zeros(delay_start/dt+1,1); % zeropad before TMS delivery
train_E = [train_E; repmat(pulse_extend,nump-1,1)]; % Append TMS pulses
train_E = [train_E; TMS_E; zeros(length(train_t)-length(train_E)-length(TMS_E),1)];


%% GRAPHICAL ANALYSIS
figure
plot(TMS_t, TMS_E)
title('Generated Biphasic E-Field Waveform')

figure
plot(train_t, train_E)
title('Generated pulse train')

%% Downsampling if dt=0.025us
if STEP_type==2
    train_E = train_E(1:5:end);
    train_t = train_t(1:5:end) ; 
    step = 0.025;
end

%% Normalization
train_E = train_E/max(train_E);

%% Save timing information
timing = [ipi;delay_start;nump;step];

%% Save train
if ~exist('../../Results/TMS_Waveform','dir')
    mkdir('../../Results/TMS_Waveform');
end
save(['../../Results/TMS_Waveform' filesep 'TMS_E_train.txt'], 'train_E','-ascii');
save(['../../Results/TMS_Waveform' filesep 'TMS_t_train.txt'], 'train_t','-ascii');
save(['../../Results/TMS_Waveform' filesep 'TMS_timing.txt'], 'timing', '-ascii');

disp('Successfully generated the TMS waveform!');
end