# speech-recognition

* Currently data is stored at `data/audio` and `data/label`. Maybe can follow LibriSpeech directory structure.
* `AudioDataset` - read data from directory and convert to spectogram. Variable length.
* `dataloader_audio.collate_fn` pad sequence. Yet to check compatiblity with nn.
* `utils.TextProcess` to clean text. Currently include to lower case, remove punctuations, numbers(including years) to words.