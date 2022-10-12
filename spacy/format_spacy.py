# -*- coding: utf-8 -*-

import codecs
import os

def iob_iobes(tags):
    """
    IOB -> IOBES
    """
    new_tags = []
    for i, tag in enumerate(tags):
        if tag == 'O':
            new_tags.append(tag)
        elif tag.split('-')[0] == 'B':
            if i + 1 != len(tags) and \
               tags[i + 1].split('-')[0] == 'I':
                new_tags.append(tag)
            else:
                new_tags.append(tag.replace('B-', 'S-'))
        elif tag.split('-')[0] == 'I':
            if i + 1 < len(tags) and \
                    tags[i + 1].split('-')[0] == 'I':
                new_tags.append(tag)
            else:
                new_tags.append(tag.replace('I-', 'E-'))
        else:
            raise Exception('Invalid IOB format!')
    return new_tags

def iob2(tags, words):
    """
    Check that tags have a valid IOB format.
    Tags in IOB1 format are converted to IOB2.
    """
    for i, tag in enumerate(tags):
        if tag == 'O':
            continue
        split = tag.split('-')
        if len(split) != 2 or split[0] not in ['I', 'B']:
            return False
        if split[0] == 'B':
            continue
        elif i == 0 or tags[i - 1] == 'O':  # conversion IOB1 to IOB2
            tags[i] = 'B' + tag[1:]
        elif tags[i - 1][1:] == tag[1:]:
            continue
        else:  # conversion IOB1 to IOB2
            tags[i] = 'B' + tag[1:]
    return True

def load_sentences(path, lower, zeros):
    """
    Load sentences. A line must contain at least a word and its tag.
    Sentences are separated by empty lines.
    """
    lengths = []
    sentences = []
    sentence = []
    for idx, line in enumerate(codecs.open(path, 'r', 'utf-8')):
        line = zero_digits(line.rstrip()) if zeros else line.rstrip()
        if not line:
            if len(sentence) > 0:
                if 'DOCSTART' not in sentence[0][0]:
                    sentences.append(sentence)
                    lengths.append(len(sentence))
                sentence = []
            else:
                print('0 sentence')
        else:
            word = line.split()
            assert len(word) >= 2, print(line)

            sentence.append(word)
    if len(sentence) > 0:
        if 'DOCSTART' not in sentence[0][0]:
            sentences.append(sentence)
            lengths.append(len(sentence))

    return sentences


def update_tag_scheme(sentences, tag_scheme):
    """
    Check and update sentences tagging scheme to IOB2.
    Only IOB1 and IOB2 schemes are accepted.
    """
    for i, s in enumerate(sentences):
        tags = [w[-1] for w in s]
        # Check that tags are given in the IOB format
        
        if not iob2(tags, [w[0] for w in s]):
            s_str = '\n'.join(' '.join(w) for w in s)
            raise Exception('Sentences should be given in IOB format! ' +
                            'Please check sentence %i:\n%s' % (i, s_str))
        if tag_scheme == 'iob':
            # If format was IOB1, we convert to IOB2
            for word, new_tag in zip(s, tags):
                word[-1] = new_tag
        elif tag_scheme == 'iobes':
            new_tags = iob_iobes(tags)
            for word, new_tag in zip(s, new_tags):
                word[-1] = new_tag
        else:
            raise Exception('Unknown tagging scheme!')



# get all files in a dossier
def get_data(file_path):

    data = []
        
    sentences = load_sentences(file_path, lower=False, zeros=False)
    update_tag_scheme(sentences, 'iobes')

    for sentence in sentences:
        entities = []

        entry = {'text': '', 'entities': [], 'entity_text': [], 'entity_type': []}
        entity_text = ''
        entity_type = 'none'
        idx_start, idx_end = 0, 0
        for line in sentence:
            try:
                text, _, label = line
            except:
                text, label = line

            if len(entry['text']) == 0:
                entry['text'] = text.strip()
            else:
                entry['text'] += ' ' + text.strip()

            if ('B-' in label):
                entity_text = text
                entity_type = label[2:]
                idx_end = idx_start + len(entity_text)

            if ('S-' in label):
                entity_text = text
                entity_type = label[2:]
                idx_end = idx_start + len(entity_text)
                entry['text'] = entry['text'].strip()

                try:
                    assert entry['text'][idx_start:idx_end] == entity_text
                except:
                    import pdb;pdb.set_trace()

                entities.append((idx_start, idx_end, entity_type))

                entity_text = ''
                entity_type = ''
                idx_start = len(entry['text']) + 1

            if ('I-' in label):
                entity_text += ' ' + text
                entity_type = label[2:]
                idx_end = idx_start + len(entity_text)

            if ('E-' in label):
                entity_text += ' ' + text
                entity_type = label[2:]
                idx_end = idx_start + len(entity_text)

                entry['text'] = entry['text'].strip()

                try:
                    assert entry['text'][idx_start:idx_end] == entity_text
                except:
                    import pdb;pdb.set_trace()
                entities.append((idx_start, idx_end, entity_type))

                entity_text = ''
                entity_type = ''
                idx_start = len(entry['text']) + 1

            if label == 'O':
                if len(entity_text) > 1:
                    entry['text'] = entry['text'].strip()

                    try:
                        assert entry['text'][idx_start:idx_end] == entity_text
                    except:
                        import pdb;pdb.set_trace()

                    entities.append((idx_start, idx_end, entity_type))
                    entity_type = ''

                entity_text = ''
                entity_type = ''
                idx_start = len(entry['text']) + 1

        data.append((entry['text'], {'entities': entities}))
    return data