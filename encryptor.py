import argparse
import string
import sys
import json
from collections import Counter


indexes_lower_case = {string.ascii_lowercase[i]: i for i in range(len(string.ascii_lowercase))}
indexes_upper_case = {string.ascii_uppercase[i]: i for i in range(len(string.ascii_uppercase))}

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers()
decode = subparsers.add_parser('decode')
encode = subparsers.add_parser('encode')
hack = subparsers.add_parser('hack')
train = subparsers.add_parser('train')

encode.set_defaults(mode='encode')
encode.add_argument('--cipher')
encode.add_argument('--key')
encode.add_argument('--input-file')
encode.add_argument('--output-file')

decode.set_defaults(mode='decode')
decode.add_argument('--cipher')
decode.add_argument('--key')
decode.add_argument('--input-file')
decode.add_argument('--output-file')

hack.set_defaults(mode='hack')
hack.add_argument('--input-file')
hack.add_argument('--output-file')
hack.add_argument('--model-file')

train.set_defaults(mode='train')
train.add_argument('--text-file')
train.add_argument('--model-file')

parser_arguments = parser.parse_args()


def one_digit_cipherator(slide, digit, mode, is_upper, cipher, counter):
    alphabet_size = len(string.ascii_lowercase)
    if cipher == 'caesar':
        if not is_upper:
            return string.ascii_lowercase[(indexes_lower_case[digit] + int(slide) * mode) % alphabet_size]
        else:
            return string.ascii_uppercase[(indexes_upper_case[digit] + int(slide) * mode) % alphabet_size]
    elif cipher == 'vigenere':
        if not is_upper:
            return string.ascii_lowercase[
                (indexes_lower_case[digit] + (indexes_lower_case[slide[counter % len(slide)]]) * mode) % alphabet_size]
        else:
            return string.ascii_uppercase[
                (indexes_upper_case[digit] + (indexes_upper_case[slide[counter % len(slide)]]) * mode) % alphabet_size]


def coding(input, slide, action, cipher):
    counter = 0
    text = []
    for i in input:
        if i.islower() or i.isupper():
            is_upper = False
            if i.isupper():
                is_upper = True
            text.append(one_digit_cipherator(slide, i, action, is_upper, cipher, counter))
            counter += 1
        else:
            text.append(i)
    return ''.join(text)


def train(text_to_train):
    size = 0
    statistics = dict()
    for i in text_to_train:
        ilow = i.lower()
        if ilow.isalpha():
            size += 1
            # or we can do this code : if i.isalpha():
            if ilow in statistics:
                statistics[ilow] += 1
            else:
                statistics[ilow] = 1
    for i in statistics:
        statistics[i] /= size
    return statistics


def difference(correct_dict, unhacked_dict, slide):
    diff = 0.0
    for i in string.ascii_lowercase:
        slided_i = one_digit_cipherator(slide, i, -1, False, 'caesar', 10)
        if i in correct_dict and slided_i in unhacked_dict:
            diff += (correct_dict[i] - unhacked_dict[slided_i]) ** 2
    return diff


def hacker(text_to_hacking, hacking_model):
    statistic = train(text_to_hacking)
    alphabet_size = len(string.ascii_lowercase)
    min_key = 0
    min_diff = difference(hacking_model, statistic, 0)
    for i in range(1, alphabet_size):
        curr_diff = difference(hacking_model, statistic, i)
        if curr_diff < min_diff:
            min_key = i
            min_diff = curr_diff
    hacked_text = coding(text_to_hacking, min_key, 1, 'caesar')
    return hacked_text


def reading(file):
    with open(file, 'r') as reading_file:
        txt = reading_file.read()
    return txt


def writing(file, text):
    with open(file, 'w') as new_file:
        new_file.write(text)


def coding_and_encoding(arguments):
    action = 1
    if arguments.mode == 'decode':
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


def training(arguments):
    if arguments.text_file:
        text = reading(arguments.text_file)
    else:
        text = sys.stdin.read()
    stats = train(text)
    writing(arguments.model_file, json.dumps(stats, indent=4))


def hacking(arguments):
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


if parser_arguments.mode == 'encode' or parser_arguments.mode == 'decode':
    coding_and_encoding(parser_arguments)

elif parser_arguments.mode == 'train':
    training(parser_arguments)

elif parser_arguments.mode == 'hack':
    hacking(parser_arguments)

    
