import argparse
import string
import sys
import json

parser = argparse.ArgumentParser()
parser.add_argument("mode", type=str)
parser.add_argument("--cipher")
parser.add_argument("--key")
parser.add_argument("--input-file")
parser.add_argument("--output-file")
parser.add_argument("--text-file")
parser.add_argument("--model-file")
arguments = parser.parse_args()


def one_digit_cipherator(slide, digit, mode, letter, cipher, counter):
    l = ord(letter)
    if cipher == 'caesar':
        return chr((ord(digit) - ord(letter) + int(slide) * mode) % 26 + ord(letter))
    elif cipher == 'vigenere':
        return chr((ord(digit) + (ord(slide[counter % len(slide)]) - l) * mode - l) % 26 + ord(letter))


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


if arguments.mode == "encode" or arguments.mode == "decode":
    action = 1
    new_txt = ''
    if arguments.mode == "decode":
        action = -1
    if arguments.input_file:
        file = open(arguments.input_file, 'r')
        txt = file.read()
        new_txt = coding(txt, arguments.key, action, arguments.cipher)
        file.close()
        if arguments.output_file:
            new_file = open(arguments.output_file, 'w')
            new_file.write(new_txt)
            new_file.close()
        else:
            print(new_txt)
    else:
        txt = sys.stdin.read()
        new_txt = coding(txt, arguments.key, action, arguments.cipher)
        if arguments.output_file:
            new_file = open(arguments.output_file, 'w')
            new_file.write(new_txt)
            new_file.close()
        else:
            print(new_txt)

if arguments.mode == "train":
    text = ''
    if arguments.text_file:
        file = open(arguments.text_file, 'r')
        text = file.read()
        file.close()
    else:
        text = sys.stdin.read()
    stats = train(text)
    stats_file = open(arguments.model_file, 'w')
    stats_file.write(json.dumps(stats, indent=4))
    stats_file.close()

if arguments.mode == "hack":
    with open(arguments.model_file, 'r') as f:
        model = json.load(f)
    if arguments.input_file:
        file = open(arguments.input_file, 'r')
        txt = file.read()
        new_txt = hacker(txt, model)
        file.close()
        if arguments.output_file:
            new_file = open(arguments.output_file, 'w')
            new_file.write(new_txt)
            new_file.close()
        else:
            print(new_txt)
    else:
        txt = sys.stdin.read()
        new_txt = hacker(txt, model)
        if arguments.output_file:
            new_file = open(arguments.output_file, 'w')
            new_file.write(new_txt)
            new_file.close()
        else:
            print(new_txt)
