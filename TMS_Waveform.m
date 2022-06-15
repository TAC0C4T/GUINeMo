function TMS_Waveform()
%% Generate TMS pulse trains and write them in a file to be used in the
% NEURON simulation.

% Receive TMS parameters
% 1: Monophasic, 2: Biphasic, 3: Custom**
TMS_type = menu('Choose TMS pulse type:','Monophasic','Biphasic','Rudy Custom');
STEP_type = menu('Choose step time (us) :','5','25 (Default)');

%%
prompt = {'\bfEnter the inter-pulse interval in ms:',...
    '\bf Enter the number of pulses:'};

dlgtitle = 'TMS Parameters';
dims = [1 92];
opts.Interpreter = 'tex';
opts.WindowStyle = 'normal';
definput = {'1000','10'};
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
%% Read TMS single pulse file
dt = 0.005;
if TMS_type == 1
    load(['./original_waveforms' filesep 'TMS_mono.mat']);
elseif TMS_type == 2
    load(['./original_waveforms' filesep 'TMS_bi.mat']);
else
    custom_TMS_type = menu('Choose TMS pulse type:','Custom Monophasic(NOT READY)','Custom Biphasic','Custom Rectangular','Custom Boost(NOT READY)');
    prompt = {'\bfEnter pulse length in ms:',...
    '\bfEnter the desired duty cycle percentage:',...
    '\bfEnter the desired duty cycle change rate: \rm Leave as 0 if you want the same duty cycle for all pulses.'};
    dlgtitle = 'TMS Parameters';
    dims = [1 92];
    opts.Interpreter = 'tex';
    opts.WindowStyle = 'normal';
    definput2 = {'0.15','100','0'};
    while 1
        answer2 = inputdlg(prompt,dlgtitle,dims,definput2,opts);
        pulseFrequency = 1/(str2double(answer2{1})*2);
        pulseMod = str2double(answer2{2});
        pulseModChange = str2double(answer2{3});
            if ~isnan(pulseFrequency) && ~isnan(pulseMod) && ~isnan(pulseModChange) && pulseFrequency>0 && pulseMod>0 && pulseModChange>=0
        break
            end
        definput2 = answer2;
        if isnan(pulseFrequency)
            definput2{1} = 'Wrong format!';
        elseif pulseFrequency<=0
            definput2{1} = 'Value should be positive!';
        end
        if isnan(pulseMod)
            definput2{2} = 'Wrong format!';
        elseif pulseMod<0 || pulseMod>100
            definput2{2} = 'Value must be between 0 and 100';
        end
        if isnan(pulseModChange)
            definput2{3} = 'Wrong format!';
        elseif pulseModChange<0 || pulseModChange>100
            definput2{3} = 'Value must be between 0 and 100';
        end
    end
    
    if custom_TMS_type == 1
    %% WIP NEED TO ADD MONOPHASIC HERE
    elseif custom_TMS_type == 2
    %% Biphasic Pulse
        TMS_t = (0:dt:(str2double(answer2{1})*2)+0.01);
        currentPulse = sin(2*pi*pulseFrequency*(TMS_t-0.01));    %sin with a phase shift of two samples to account for zero values.
        currentPulseArray = repmat(currentPulse,nump,1);
    
    
        halfLength = round(length(currentPulse)/2) - 2;
        Length = length(currentPulse) - 2;
    
        for i = 1 : nump
            if pulseMod < 100
                pulseShift = round((100 - pulseMod)*str2double(answer2{1})/dt/100);
                currentPulseArray(i,halfLength +2 - pulseShift: halfLength +1) = 0;
                currentPulseArray(i,Length +2 - pulseShift:end) = 0;
            end
            pulseMod = pulseMod - pulseModChange;
            if pulseMod < 0
                pulseMod = 0;
            end
        end
       
        TMS_E = diff(currentPulseArray,1,2);
        
        TMS_E(:,1) = 0;
        TMS_E(:,2) = (TMS_E(:,1)+TMS_E(:,3))/2;                  %prevents jumping to max value from zero
        %TMS_E = TMS_E.* (linspace(1,0.8,size(TMS_E,2)));         %Imitating recorded waveforms taper
    
        localMaxE = 0;
        for i = 2:size(TMS_E,2)
            if TMS_E(1,i-1) > localMaxE && TMS_E(1,i) < TMS_E(1,i-1)
                localMaxE = TMS_E(1,i-1);
                break
            end
        end
    
        TMS_E = TMS_E./localMaxE;                   %normalizing results
        
        for j = 1:nump
            for i = 1:(size(TMS_E,2)-1)             %trimming assymptotic peaks down
                if TMS_E(j,i) > 1                   %(could be made harsher)
                    TMS_E(j,i) = 1;
                elseif TMS_E(j,i) < -1
                    TMS_E(j,i) = -1;
                end
            end
        end
    elseif custom_TMS_type == 3
    %% Rectangular Pulse
        TMS_t = (0:dt:(str2double(answer2{1})*3)+0.01);
        TMS_E = ones(nump, length(TMS_t));
        recoveryOvershoot = -0.2;
        
        for j = 1:nump
            if pulseMod <= 0
                TMS_E(j,:) = 0;
            else
                for i = round(length(TMS_t)*pulseMod/300):length(TMS_t)
                    TMS_E(j,i) = recoveryOvershoot;
                end
            end
            pulseMod = pulseMod - pulseModChange;
        end
    else
    %% WIP NEED TO ADD BOOST PULSE
    end

    if size(TMS_E,2) < round(ipi/dt)
        fieldExtend = zeros(nump, round(ipi/dt) - size(TMS_E,2));
        TMS_E = [TMS_E, fieldExtend];
    end
    
    if length(TMS_t) < size(TMS_E,2)
        timeExtend = (max(TMS_t)+dt : dt : max(TMS_t)+((length(TMS_E)-length(TMS_t))*dt));
        TMS_t = [TMS_t, timeExtend];
    end
    
    TMS_E = TMS_E';
    TMS_t = TMS_t';
end

if TMS_type == 1 || TMS_type == 2
    %% Generate pulse train (ORIGINAL)
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
else
    %% Generate pulse train (Custom)
    step = 0.005;
    if size(TMS_E,2) > round(ipi/dt)
        error('Inter-pulse interval cannot be shorter than TMS pulse duration.');
    end
    delay_start = 40;
    ipi = round(ipi/dt)*dt;
    train_length = (2*delay_start) + (nump-1)*ipi; % in ms
    TMS_E_Reshape = reshape(TMS_E,[],1);
    
    train_E = [zeros(delay_start/dt+1,1); TMS_E_Reshape];
    train_E(round(train_length/dt)+1:end) = [];  %because each pulse has already been extended, here I'm removing the long tail of zeros
    train_t = (0:dt:((length(train_E)-1)*dt))';
end

%% GRAPHICAL ANALYSIS
figure
plot(TMS_t,TMS_E)
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