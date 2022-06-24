import os
import json

import argparse
from tqdm import tqdm
import functools
from multiprocessing import Pool

def load_dic(path):
    dic = {}
    with open(path, 'r') as f:
        for k in f.readlines():
            k = k.strip()
            if len(k)==0: continue
            k = k.split()
            dic[k[0]] = k[1]
    return dic

def path_exists(path):
    if os.path.exists(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"Path exists check:{path} is not a valid path.")

def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if (uchar >= u'\u4e00') and (uchar <= u'\u9fa5'):
        return True
    else:
        return False

def zh2letter(text, save_path, dictionary):
    with open(save_path, 'w') as f:
        for line in tqdm(text):
            if isinstance(line, dict) and 'content' in line: line = line['content']
            char_set = set(list(line))
            newline = line
            for char in char_set:
                if is_chinese(char):
                    newline = newline.replace(char, ' '+dictionary.get(char, '')+' ')
            f.write(' '.join(newline.split())+'\n')

def read_text(path):
    print('reading text from file ', path)
    with open(path, 'r') as f:
        text = f.readlines()
    return text

def shift_vocab(vocab, key):
    dic = {}
    for i in range(len(vocab)):
        dic[vocab[i]] = vocab[(i+key) % len(vocab)]
    return dic

def monophonic(plain_text, vocab, shifted_vocab):
    cipher_text = []
    for c in plain_text:
        if c in vocab:
            cipher_text.append(shifted_vocab[c])
        else:
            cipher_text.append(c)
    return ''.join(cipher_text)

def encipher(input_path, key, output_path):
    vocab = 'abcdefghijklmnopqrstuvwxy'
    text = read_text(input_path)
    cipher_text = []
    shifted_vocab = shift_vocab(vocab, key)
    #monocipher = functools.partial(monophonic, vocab=vocab, shifted_vocab=shifted_vocab)
    #with Pool(1) as pool:
    #    cipher_text = list(pool.map(monocipher, text))
    #assert len(cipher_text) == len(text)
    print('generating src-rot-{} with cipher key {}'.format(key, key))
    with open(output_path, 'w') as f:
        for k in tqdm(text):
            f.write(monophonic(k, vocab, shifted_vocab))
            del k

def write_file(src, trg):
    with open(src, 'r') as f1, open(trg, 'w') as f2:
        for k in f1.readlines(): f2.write(k)

def parserr():
    
    parser = argparse.ArgumentParser(
        prog="encipher",
        usage="%(prog)s --input --keys [options]",
        description="Arguments for generating cipher text from an given plaintext.",
    )

    parser.add_argument('-i', '--input', type=path_exists, required=True, help='input file dir.')
    parser.add_argument('-o', '--output', type=str, required=True, help='output file dir.')
    parser.add_argument('-s', '--src', type=str, required=False, help='src language.')
    parser.add_argument('-t', '--trg', type=str, required=False, help='trg language.')
    parser.add_argument('-v', '--vocab-path', type=path_exists, required=True, help='vocab file path.')
    parser.add_argument('--keys', nargs="+", type=int, required=True, help='list of keys for encipherment.')

    return parser


if __name__ == "__main__":
    parser = parserr()
    args = parser.parse_args()
    dic = load_dic(args.vocab_path)
    splits = ['train', 'valid', 'test']
    if not os.path.exists(args.output):
        os.mkdir(args.output)
    for split in splits:
        src_name = "{}.{}-{}.{}".format(split, args.src, args.trg, args.src)
        trg_name = "{}.{}-{}.{}".format(split, args.src, args.trg, args.trg)
        save_src = os.path.join(args.output, src_name)
        save_trg = os.path.join(args.output, trg_name)
        plaintext_src = read_text(os.path.join(args.input, src_name))
        write_file(os.path.join(args.input, trg_name), save_trg)
        zh2letter(plaintext_src, save_src, dic)
        del plaintext_src
        for key in args.keys:
            write_file(save_trg, os.path.join(args.output, "{}.{}{}-{}.{}".format(split, args.src, key, args.trg, args.trg)))
            save_src_cipher = os.path.join(args.output, "{}.{}{}-{}.{}{}".format(split, args.src, key, args.trg, args.src, key))
            encipher(save_src, key, save_src_cipher)
            write_file(save_src, os.path.join(args.output, "{}.{}{}-{}.{}".format(split, args.src, key, args.src, args.src)))
            write_file(save_src_cipher, os.path.join(args.output, "{}.{}{}-{}.{}{}".format(split, args.src, key, args.src, args.src, key)))
        
