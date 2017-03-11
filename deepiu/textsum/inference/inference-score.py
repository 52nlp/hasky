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

def predict(predictor, input_text, text):
  input_word_ids = _text2ids(input_text, INPUT_TEXT_MAX_WORDS)
  print('input_word_ids', input_word_ids, 'len:', len(input_word_ids))
  print(text2ids.ids2text(input_word_ids))
  word_ids = _text2ids(text, INPUT_TEXT_MAX_WORDS)
  print('word_ids', word_ids, 'len:', len(word_ids))
  print(text2ids.ids2text(word_ids))

  timer = gezi.Timer()
  exact_score = predictor.inference(['exact_score'], 
                                    feed_dict= {
                                      'seq2seq/model_init_1/input_text:0': [input_word_ids],
                                      'seq2seq/run/text_1:0': [word_ids]
                                      })
  
  print('exact_score:', exact_score)
  print('calc score time(ms):', timer.elapsed_ms())

def main(_):
  text2ids.init()
  predictor = melt.Predictor(FLAGS.model_dir)
  predict(predictor, '���������һ�Ը�Ů�ڿ�����ջ�͸����˿¶�δ���������ڿ�Ů��-�Ա���', '��˿�ڿ�Ů')
  predict(predictor, '���������һ�Ը�Ů�ڿ�����ջ�͸����˿¶�δ���������ڿ�Ů��-�Ա���', '�Ը�Ů�ڿ�')
  predict(predictor, '���������һ�Ը�Ů�ڿ�����ջ�͸����˿¶�δ���������ڿ�Ů��-�Ա���', 'ƻ������')
  predict(predictor, '���������һ�Ը�Ů�ڿ�����ջ�͸����˿¶�δ���������ڿ�Ů��-�Ա���', '�Ը�͸���ڿ�')
  predict(predictor, '����������ʵ��С��ô��,����������ʵ��С���δ�ʩ', '�߲�')
  predict(predictor, '����������ʵ��С��ô��,����������ʵ��С���δ�ʩ', '����')
  predict(predictor, '����������ʵ��С��ô��,����������ʵ��С���δ�ʩ', '������ֲ')
  predict(predictor, '����������ʵ��С��ô��,����������ʵ��С���δ�ʩ', 'С����ͼƬ')
  predict(predictor, '����������ʵ��С��ô��,����������ʵ��С���δ�ʩ', '����')
  predict(predictor, '����������ʵ��С��ô��,����������ʵ��С���δ�ʩ', 'С����')

if __name__ == '__main__':
  tf.app.run()
