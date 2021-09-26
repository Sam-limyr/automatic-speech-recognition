import os
import torch
import torchaudio
import torchaudio.transforms as T
from utils import TextProcess

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

class AudioDataset(torch.utils.data.Dataset):

    # parameters = {
    #     "sample_rate": 16000, "n_feats": 81,
    #     "specaug_rate": 0.5, "specaug_policy": 3,
    #     "time_mask": 70, "freq_mask": 15     }

    def __init__(self, audio_dir, label_dir, transform=None):
        labels = []
        for file in os.listdir(label_dir):
            if file.endswith('.txt'):
                filepath = os.path.join(label_dir, file)
                with open(filepath) as f_input:
                    labels.append(f_input.read())
        self.labels = labels
        self.audio_dir = audio_dir
        self.transform = torch.nn.Sequential(
            T.MFCC()
            # T.LogMelSpec(sample_rate=sample_rate, n_mels=n_feats,  win_length=160, hop_length=80)
        )

    def __len__(self):
        return len(os.listdir(self.audio_dir))

    def __getitem__(self, index):
        audio_path = os.path.join(self.audio_dir, os.listdir(self.audio_dir)[index])
        waveform, sample_rate = torchaudio.load(audio_path)
        spectogram = self.transform(waveform)

        label = self.text_process.text_to_int_sequence(self.labels.iloc[index])
        return spectogram, label


# def collate_fn(data):
#     spectograms = []
#     labels = []
#     input_lengths = []
#     label_lengths = []

#     for (spectogram, label, input_length, label_length) in data:
        







if __name__ == '__main__':
    AUDIO_DIR = 'data/audio'
    LABEL_DIR = 'data/label'

    training_data = AudioDataset(AUDIO_DIR, LABEL_DIR)
    # test_data = AudioDataset(AUDIO_DIR, LABEL_DIR)

    print(len(training_data))

    # train_dataloader = torch.utils.data.DataLoader(training_data, batch_size=64, shuffle=True)
    # test_dataloader = torch.utils.data.DataLoader(test_data, batch_size=64, shuffle=True)