#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse, sys, difflib, re

#
# command line arguments
#
arg_parser = argparse.ArgumentParser('''Merges two texts.''')

# txt file 1
arg_parser.add_argument('-t', '--text', type=argparse.FileType ( 'r' ), nargs='?', metavar='TXT', help='Text file 1: OCRopus (i.e. "better" text)', required=True)

# txt file 2
arg_parser.add_argument('-T', '--Text', type=argparse.FileType ( 'r' ), nargs='?', metavar='TXT', help='Text file 2: Tesseract (i.e. "inferior" text)', required=True)

# gold file
arg_parser.add_argument('-g', '--gold', type=argparse.FileType ( 'r' ), nargs='?', metavar='LEX', help='Gold lexicon', required=True)

# output file
arg_parser.add_argument('output', type=argparse.FileType ( 'w' ), nargs='?', metavar='FILE', help='Output', default=sys.stdout)

args = arg_parser.parse_args ()

#
# read in inputs
#

clean_gold_re = re.compile(u"^\W*(.*\w)\W*$", re.U)

# gold lex
gold = {}
for line in args.gold:
    fields = line.strip().decode("utf-8").split(u'\t')

    # hacks for handling non-standard orthography
    if len(fields) > 1:
        golds = set([fields[0],fields[0].replace(u"ſ",u"s"), clean_gold_re.sub(u"\\1",fields[0]), clean_gold_re.sub(u"\\1",fields[0].replace(u"ſ",u"s"))])
        for g in golds:
            if not gold.has_key(g):
                gold[g] = 0
            gold[g] += int(fields[1])

# text 1: ocropus
lines = []
for line in args.text:
    text = []
    word = u""
    line = line.strip().decode("utf-8")
    if line:
        for c in line:
            if not c or c == u" ":
                if len(word) > 0:
                    text.append(word)
                word = u""
                continue
            word += c
        if word:
            text.append(word)
        lines.append(text)

# text 2: tesseract
Lines = []
for line in args.Text:
    text = []
    word = u""
    line = line.strip().decode("utf-8")
    if line:
        for c in line:
            if not c or c == u" ":
                if len(word) > 0:
                    text.append(word)
                word = u""
                continue
            word += c
        if word:
            text.append(word)
        Lines.append(text)

#
# perform diff
#
length = len(lines)
if len(Lines) < length:
    length = len(Lines)
for k in range(0,length):
    text = lines[k]
    Text = Lines[k]

    diff = difflib.SequenceMatcher(None, text, Text)

    output = []

    for tag, i1, i2, j1, j2 in diff.get_opcodes():
        if tag == "replace":
            left = text[i1:i2]
            right = Text[j1:j2]
            if len(left) != len(right):
                #
                # unequal size: fallback to character level
		# searching for equal subsequences
                lstream = u" ".join(lword for lword in left)
                rstream = u" ".join(rword for rword in right)
                diff2 = difflib.SequenceMatcher(None, lstream, rstream)
                loutput = u""
                routput = u""
                for tag2, I1, I2, J1, J2 in diff2.get_opcodes():
                    lseq = lstream[I1:I2]
                    rseq = rstream[J1:J2]
                    if tag2 == "replace" or tag2 == "equal":
                        if len(lseq) < len(rseq):
                           min_len = len(lseq)
                           llonger = False
                        else:
                           min_len = len(rseq)
                           llonger = True
                        for i in range(0,min_len):
                            if lseq[i] == u" ":
                                if gold.has_key(loutput):
                                    output.append(loutput)
                                elif gold.has_key(routput):
                                    output.append(routput)
                                else:
                                    # again: hacks for non-standard orthography
                                    lnorm = clean_gold_re.sub(u"\\1",loutput)
                                    rnorm = clean_gold_re.sub(u"\\1",routput)
                                    if lnorm and gold.has_key(lnorm):
                                        output.append(loutput)
                                    elif rnorm and gold.has_key(rnorm):
                                        output.append(routput)
                                    else:
                                        output.append(loutput)
                                loutput = u""
                                routput = u""
                                continue
                            loutput += lseq[i]
                            routput += rseq[i] 
                        if llonger:
                            for i in range(min_len,len(lseq)):
                                if lseq[i] == u" ":
                                    if gold.has_key(loutput):
                                        output.append(loutput)
                                    elif gold.has_key(routput):
                                        output.append(routput)
                                    else:
                                        lnorm = clean_gold_re.sub(u"\\1",loutput)
                                        rnorm = clean_gold_re.sub(u"\\1",routput)
                                        if lnorm and gold.has_key(lnorm):
                                            output.append(loutput)
                                        elif rnorm and gold.has_key(rnorm):
                                            output.append(routput)
                                        else:
                                            output.append(loutput)
                                    loutput = u""
                                    routput = u""
                                    continue
                                loutput += lseq[i]
                        else:
                            for i in range(min_len,len(rseq)):
                                routput += rseq[i]
                    elif tag2 == "insert":
                        for i in range(0,len(rseq)):
                            if rseq[i] != u" ":
                                routput += rseq[i]
                    elif tag2 == "delete":
                        for i in range(0,len(lseq)):
                            if lseq[i] == u" ":
                                if gold.has_key(loutput):
                                    output.append(loutput)
                                elif gold.has_key(routput):
                                    output.append(routput)
                                else:
                                    lnorm = clean_gold_re.sub(u"\\1",loutput)
                                    rnorm = clean_gold_re.sub(u"\\1",routput)
                                    if lnorm and gold.has_key(lnorm):
                                        output.append(loutput)
                                    elif rnorm and gold.has_key(rnorm):
                                        output.append(routput)
                                    else:
                                        output.append(loutput)
                                loutput = u""
                                routput = u""
                                continue
                            loutput += lseq[i]
                if loutput:
                    if gold.has_key(loutput):
                        output.append(loutput)
                    elif gold.has_key(routput):
                        output.append(routput)
                    else:
                        lnorm = clean_gold_re.sub(u"\\1",loutput)
                        rnorm = clean_gold_re.sub(u"\\1",routput)
                        if lnorm and gold.has_key(lnorm):
                            output.append(loutput)
                        elif rnorm and gold.has_key(rnorm):
                            output.append(routput)
                        else:
                            output.append(loutput)
            else:
                #
                # step 1: lookup in gold lexikon
                for i in range(0,len(left)):
                    #sys.stderr.write("1st try: %s,%s\n" % (left[i].encode("utf-8"),right[i].encode("utf-8")) )
                    if gold.has_key(left[i]):
                        if gold.has_key(right[i]):
                            if gold[left[i]] >= gold[right[i]]:
                                output.append(left[i])
                            else:
                                output.append(right[i])
                        else:
                            output.append(left[i])
                    elif gold.has_key(right[i]):
                        output.append(right[i])
                    else:
                        lnorm = clean_gold_re.sub(u"\\1",left[i])
                        rnorm = clean_gold_re.sub(u"\\1",right[i])
                        #sys.stderr.write("2nd try: %s,%s\n" % (lnorm.encode("utf-8"),rnorm.encode("utf-8")) )
                        if lnorm and gold.has_key(lnorm):
                            output.append(left[i])
                        elif rnorm and gold.has_key(rnorm):
                            output.append(right[i])
                        else:
                            output.append(left[i])

        elif tag == "insert":
            # TODO: something more clever?
            pass
        elif tag == "delete":
            # TODO: something more clever?
            for i in range(i1, i2):
                output.append(text[i])
        else:
            for i in range(i1, i2):
                output.append(text[i])

    args.output.write("%s\n" % u" ".join(output).replace(u"\n ", u"\n").encode("utf-8"))
