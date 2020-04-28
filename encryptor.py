import argparse
import string
import sys
import json

parser = argparse.ArgumentParser()
# parser.add_argument("mode", type=str)

subparsers = parser.add_subparsers()
decode = subparsers.add_parser('decode')
encode = subparsers.add_parser('encode')
hack = subparsers.add_parser('hack')
train = subparsers.add_parser('train')

encode.set_defaults(mode='encode', func=encode)
encode.add_argument("--cipher")
encode.add_argument("--key")
encode.add_argument("--input-file")
encode.add_argument("--output-file")

decode.set_defaults(mode='decode')
decode.add_argument("--cipher")
decode.add_argument("--key")
decode.add_argument("--input-file")
decode.add_argument("--output-file")

hack.set_defaults(mode='hack')
hack.add_argument("--input-file")
hack.add_argument("--output-file")
hack.add_argument("--model-file")

train.set_defaults(mode='train')
train.add_argument("--text-file")
train.add_argument("--model-file")

arguments = parser.parse_args()


def one_digit_cipherator(slide, digit, mode, size, cipher, counter):
    l = ord(size)
    if cipher == 'caesar':
        return chr((ord(digit) - ord(size) + int(slide) * mode) % 26 + ord(size))
    elif cipher == 'vigenere':
        return chr((ord(digit) + (ord(slide[counter % len(slide)]) - l) * mode - l) % 26 + ord(size))


def coding(input_, slide_, action_, cipher_):
    counter = 0
    result = ''
    for i in input_:
        if i.islower() or i.isupper():
            letter = 'a'
            if i.isupper():
                letter = 'A'
            result += one_digit_cipherator(slide_, i, action_, letter, cipher_, counter)
            counter += 1
        else:
            result += i
    return result


def train(text_to_train):
    letters_counter = {}
    for i in string.ascii_lowercase:
        letters_counter[i] = 0
    size = 0
    text_tmp = text_to_train.lower()
    statistics = dict()
    for i in text_tmp:
        if i in string.ascii_lowercase:
            letters_counter[i] += 1  # + int(letters_counter[i])
            size += 1
    for i in string.ascii_lowercase:
        statistics[i] = letters_counter[i] / size
    return statistics


def hacker(text_to_hacking, hacking_model):
    text_to_hack = text_to_hacking.lower()
    coded = train(text_to_hack)
    coded_list = list(coded.items())
    coded_list.sort(key=lambda i: i[1])
    model_list = list(hacking_model.items())
    model_list.sort(key=lambda i: i[1])
    list_for_hack = list()
    for i in range(26):
        list_for_hack.append(abs(ord(model_list[i][0]) - ord(coded_list[i][0])))
    set_for_hack = set(list_for_hack)
    most_popular = 0
    slide = 0
    for i in set_for_hack:
        counter = list_for_hack.count(i)
        if counter > most_popular:
            most_popular = counter
            slide = i
    hacked_text = coding(text_to_hacking, slide, -1, 'caesar')
    return hacked_text


def reading(file):
    file_ = open(file, 'r')
    txt = file_.read()
    file_.close()
    return txt


def writing(file, text):
    new_file = open(file, 'w')
    new_file.write(text)
    new_file.close()


def coding_and_encoding(arguments):
    action = 1
    new_txt = ''
    if arguments.mode == "decode":
        action = -1
    if arguments.input_file:
        txt = reading(arguments.input_file)
        new_txt = coding(txt, arguments.key, action, arguments.cipher)
        if arguments.output_file:
            writing(arguments.output_file, new_txt)
        else:
            print(new_txt)
    else:
        txt = sys.stdin.read()
        new_txt = coding(txt, arguments.key, action, arguments.cipher)
        if arguments.output_file:
            writing(arguments.output_file, new_txt)
        else:
            print(new_txt)

def texting (arguments) :
    text = ''
    if arguments.text_file:
        text = reading(arguments.text_file)
    else:
        text = sys.stdin.read()
    stats = train(text)
    writing(arguments.model_file, json.dumps(stats, indent=4))

def hacking (arguments) :
    with open(arguments.model_file, 'r') as f:
        model = json.load(f)
    if arguments.input_file:
        txt = reading(arguments.input_file)
        new_txt = hacker(txt, model)
        if arguments.output_file:
            writing(arguments.output_file, new_txt)
        else:
            print(new_txt)
    else:
        txt = sys.stdin.read()
        new_txt = hacker(txt, model)
        if arguments.output_file:
            writing(arguments.output_file, new_txt)
        else:
            print(new_txt)

if arguments.mode == "encode" or arguments.mode == "decode":
    coding_and_encoding(arguments)

elif arguments.mode == "train":
    texting(arguments)

elif arguments.mode == "hack":
    hacking(arguments)
