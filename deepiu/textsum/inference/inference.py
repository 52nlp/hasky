#!/usr/bin/env python
# -*- coding: gbk -*-
# ==============================================================================
#          \file   predict.py
#        \author   chenghuige  
#          \date   2016-10-19 06:54:26.594835
#   \Description  
# ==============================================================================

  
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
flags = tf.app.flags
FLAGS = flags.FLAGS

#FIXME: attention will hang..., no attention works fine
#flags.DEFINE_string('model_dir', '/home/gezi/temp/textsum/model.seq2seq.attention/', '')
flags.DEFINE_string('model_dir', '/home/gezi/temp/textsum/model.seq2seq/', '')
flags.DEFINE_string('vocab', '/home/gezi/temp/textsum/tfrecord/seq-basic.10w/train/vocab.txt', 'vocabulary file')

import sys, os
import gezi, melt
import numpy as np

from deepiu.util import text2ids

import conf  
from conf import TEXT_MAX_WORDS, INPUT_TEXT_MAX_WORDS, NUM_RESERVED_IDS, ENCODE_UNK

#TODO: now copy from prpare/gen-records.py
def _text2ids(text, max_words):
  word_ids = text2ids.text2ids(text, 
                               seg_method=FLAGS.seg_method, 
                               feed_single=FLAGS.feed_single, 
                               allow_all_zero=True, 
                               pad=False)
  word_ids = word_ids[:max_words]
  word_ids = gezi.pad(word_ids, max_words, 0)

  return word_ids

def predict(predictor, input_text):
  word_ids = _text2ids(input_text, INPUT_TEXT_MAX_WORDS)
  print('word_ids', word_ids, 'len:', len(word_ids))
  print(text2ids.ids2text(word_ids))

  timer = gezi.Timer()
  text, score = predictor.inference(['text', 'text_score'], 
                                    feed_dict= {
                                      'seq2seq/model_init_1/input_text:0': [word_ids]
                                      })
  
  for result in text:
    print(result, text2ids.ids2text(result), 'decode time(ms):', timer.elapsed_ms())
  
  timer = gezi.Timer()
  texts, scores = predictor.inference(['beam_text', 'beam_text_score'], 
                                    feed_dict= {
                                      'seq2seq/model_init_1/input_text:0': [word_ids]
                                      })

  texts = texts[0]
  scores = scores[0]
  for text, score in zip(texts, scores):
    print(text, text2ids.ids2text(text), score)

  print('beam_search using time(ms):', timer.elapsed_ms())

def main(_):
  text2ids.init()
  predictor = melt.Predictor(FLAGS.model_dir)
  predict(predictor, "������������_��������ǰ��Ա���Ƭ")
  predict(predictor, "�δﻪ�������»�Ů���� ��ͣ����̫̫(ͼ)")
  predict(predictor, "��Сͨ�Ժ�������������ڼ� ��Ʒ������լ�в�")
  predict(predictor, "ѧ���ٵ�����ʦ�� �ȶ��⾾ͷ����ͷ��ǽײ��3��סԺ")
  predict(predictor, "���������һ�Ը�Ů�ڿ�����ջ�͸����˿¶�δ���������ڿ�Ů��-�Ա���")
  predict(predictor, "����̫����ô����")
  predict(predictor, "����ף�Ŀǰ4����1�굶")
  predict(predictor, "����������ʵ��С��ô��,����������ʵ��С���δ�ʩ")
  predict(predictor, "����̫����ô����")
  predict(predictor, "����������ʵ��С��ô��,����������ʵ��С���δ�ʩ")

if __name__ == '__main__':
  tf.app.run()
