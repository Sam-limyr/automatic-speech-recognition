import os
import torch
import torchaudio
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
        self.transform = transform
        self.text_process = TextProcess()

    def __len__(self):
        return len(os.listdir(self.audio_dir))

    def __getitem__(self, index):
        audio_path = os.path.join(self.audio_dir, os.listdir(self.audio_dir)[index])
        waveform, sample_rate = torchaudio.load(audio_path)
        waveform = torch.mean(waveform, dim=0)#.unsqueeze(0)
        if self.transform:
            waveform = self.transform(waveform)

        label = self.text_process.clean_text(self.labels[index])
        # print(label)
        label = self.text_process.text_to_int_sequence(label)
        # print(label)
        label = torch.tensor(label)
        return waveform, label







def pad_sequence(batch):
    # Make all tensor in a batch the same length by padding with zeros
    batch = [item.t() for item in batch]
    batch = torch.nn.utils.rnn.pad_sequence(batch, batch_first=True, padding_value=0.)
    return batch#.permute(0, 2, 1)


def collate_fn(batch):

    # A data tuple has the form:
    # waveform, sample_rate, label, speaker_id, utterance_number

    tensors, targets = [], []

    # Gather in lists, and encode labels as indices
    for waveform, label in batch:
        tensors += [waveform]
        targets += [label]

    # Group the list of tensors into a batched tensor
    tensors = pad_sequence(tensors)
    targets = torch.stack(targets)

    return tensors, targets
        







if __name__ == '__main__':
    AUDIO_DIR = 'data/audio'
    LABEL_DIR = 'data/label'

    training_data = AudioDataset(AUDIO_DIR, LABEL_DIR)
    # test_data = AudioDataset(AUDIO_DIR, LABEL_DIR)

    print(len(training_data))

    # train_dataloader = torch.utils.data.DataLoader(training_data, batch_size=64, shuffle=True)
    # test_dataloader = torch.utils.data.DataLoader(test_data, batch_size=64, shuffle=True)