
The official code for our EMNLP 2022 paper [Breaking the Representation Bottleneck of Chinese Characters: \\ Neural Machine Translation with Stroke Sequence Modeling](https://arxiv.org/pdf/2204.00665.pdf).

## Data Preprocess
All example scripts are based the NIST Zh:arrow_right:En.

Place the NIST train, valid and test data in the `data/NIST/source` directory.
File name format should be train.zh-en.zh, train.zh-en.en and so on.

### Converting Chinese to Latinized stroke sequence and cipher with keys.

```bash
python preprocess/zh2letter-rot.py -i  path/to/input-dir -o path/to/output-dir --keys key values \
    --v path-to-chinese-stroke-dict -s src-lang -t tgt-lang
```

example:
```bash
python preprocess/zh2letter-rot.py -i /home/StrokeNet/data/NIST/source -o /home/Stroke/data/NIST/strokenet_data -v /home/StrokeNet/vocab/zh2letter.txt -s zh -t en --keys 1 2
```
This creates all parallel data in the output dir with cipher-1 and cipher-2 input.

### Preprocessing
We use subword-nmt for BPE oprations.
For learning and applying BPEs on all relevant files at once, use the `bpe.sh`
```
bach ./home/StrokeNet/scripts/bpe.sh
```
Number of BPE merge operations can be changed in bash file.

Then use `multi_binarize.sh` to generate joint multilingual dictionary and binary files for fairseq to use
```
bash ./home/StrokeNet/scripts/multi_binarize.sh
```
## Training and Evaluation
Our StrokeNet needs the support of [CipherDAug: Ciphertext based Data Augmentation for Neural Machine Translation](https://arxiv.org/pdf/2204.00665.pdf) (CDA). 
[Adaptation in CDA](https://github.com/protonish/fairseq-cipherdaug) of [FairSeq](https://github.com/pytorch/fairseq) is crucial for the working of this codebase. More details on the changes [here](https://github.com/protonish/fairseq-cipherdaug/blob/main/README.md).

In LOC/StrokeNet: 
``
git clone https://github.com/protonish/fairseq-cipherdaug.git
cd fairseq-cipherdaug
pip install --editable ./
``

### Example training script

`train.sh` comes loaded with all relevant details to set hyperparameters and start training 
```
bash /home/StrokeNet/scripts/train.sh
```
Evaluation exceeds after training is done as shown in `train.sh`

## Cite
Please consider citing us of you find any part of our code or work useful:
```
@inproceedings {kambhatla-etal-2022-cipherdaug,
   abbr="ACL",
   title = "CipherDAug: Ciphertext Based Data Augmentation for Neural Machine Translation",
   author = "Kambhatla, Nishant and
   Born, Logan and
   Sarkar, Anoop",
   booktitle = "Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics: Long Paper (To Appear)",
   month = may,
   year = "2022",
   address = "Online",
   publisher = "Association for Computational Linguistics",
   } 
```