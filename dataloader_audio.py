import os
import torch
import torchaudio
import torchaudio.transforms as T
from torch.utils.data import Dataset, DataLoader

# n_fft = 2048
# win_length = None
# hop_length = 512
# n_mels = 256
# n_mfcc = 256
# log_mels = True
# sample_rate = 14000
# mfcc_transform = T.MFCC(
#     sample_rate=sample_rate,
#     n_mfcc=n_mfcc,
#     log_mels= log_mels,
#     melkwargs={
#       'n_fft': n_fft,
#       'n_mels': n_mels,
#       'hop_length': hop_length,
#       'mel_scale': 'htk',
#     }
# )
# transform=T.MFCC(log_mels=True)

class AudioDataset(Dataset):
    def __init__(self, audio_dir, label_dir, transform=None):
        labels = []
        for file in os.listdir(label_dir):
            if file.endswith('.txt'):
                filepath = os.path.join(label_dir, file)
                with open(filepath) as f_input:
                    labels.append(f_input.read())
        self.labels = labels
        self.audio_dir = audio_dir
        self.transform = transform

    def __len__(self):
        'Denotes the total number of samples'
        return len(os.listdir(self.audio_dir))

    def __getitem__(self, index):
        'Generates one sample of data'
        audio_path = os.path.join(self.audio_dir, os.listdir(self.audio_dir)[index])
        waveform, sample_rate = torchaudio.load(audio_path)
        label = self.labels[index]
        if self.transform:
            waveform = self.transform(waveform)
        return waveform, label


# class AudioDataLoader():
#     def __init__(self, audio_dir, label_dir, batch_size):
#         self.audio_dir = audio_dir
#         self.label_dir = label_dir

#     def 





if __name__ == '__main__':
    AUDIO_DIR = 'data/audio'
    LABEL_DIR = 'data/label'

    training_data = AudioDataset(AUDIO_DIR, LABEL_DIR)
    # test_data = AudioDataset(AUDIO_DIR, LABEL_DIR)

    print(len(training_data))

    # train_dataloader = DataLoader(training_data, batch_size=64, shuffle=True)
    # test_dataloader = DataLoader(test_data, batch_size=64, shuffle=True)