import os
import torch
import torchaudio
import torchaudio.transforms as T
from utils.text import TextProcess

class AudioDataset(torch.utils.data.Dataset):
    """
    Load data from directory.
    wav audio is transformed to spectogram.
    Return (spectrogram, label, spec_len, label_len) to dataloader
    """

    def __init__(self, audio_dir, label_dir, sample_rate=16000, n_feats=128, transform=None):
        labels = []
        for file in os.listdir(label_dir): # load labels from directory to list
            if file.endswith('.txt'):
                filepath = os.path.join(label_dir, file)
                with open(filepath) as f_input:
                    labels.append(f_input.read())
        self.labels = labels
        self.audio_dir = audio_dir
        if transform:
            self.transform = transform
        else:
            self.transform = torch.nn.Sequential(
                T.MFCC(sample_rate=sample_rate, n_mfcc=n_feats, melkwargs={'n_mels': n_feats}),
                # ToTensor()
                # T.LogMelSpec(sample_rate=sample_rate, n_mels=n_feats,  win_length=160, hop_length=80)
            )
        self.text_process = TextProcess()

    def __len__(self):
        return len(os.listdir(self.audio_dir))

    def __getitem__(self, index):
        audio_path = os.path.join(self.audio_dir, os.listdir(self.audio_dir)[index])
        waveform, sample_rate = torchaudio.load(audio_path)
        waveform = torch.mean(waveform, dim=0)#.unsqueeze(0)
        spectrogram = self.transform(waveform)
        label = self.text_process.clean_text(self.labels[index])
        # print(label)
        label = self.text_process.text_to_int_sequence(label)
        # print(label)
        label = torch.tensor(label)

        spec_len = spectrogram.shape[-1] // 2
        label_len = len(label)
        print(f'Spectrogram length {spectrogram.shape}, label length {label_len}')
        return spectrogram, label, spec_len, label_len



def collate_fn(batch):

    """
    Pad sequence to spectograms and labels by batch
    A data tuple has the form:
    spectrogram, label, input_length, label_length
    """

    spectrograms = []
    labels = []
    input_lengths = []
    label_lengths = []

    # Gather in lists, and encode labels as indices
    for spectrogram, label, input_length, label_length in batch:
        spectrograms += [spectrogram.squeeze(0).transpose(0, 1)]
        labels += [label]
        input_lengths += [input_length]
        label_lengths += [label_length]

    # Group the list of tensors into a batched tensor
    spectrograms = torch.nn.utils.rnn.pad_sequence(spectrograms, batch_first=True, padding_value=0.).unsqueeze(1).transpose(2, 3)
    print(spectrograms.shape)
    labels = torch.nn.utils.rnn.pad_sequence(labels, batch_first=True) #torch.stack(labels)

    return spectrograms, labels, input_lengths, label_lengths