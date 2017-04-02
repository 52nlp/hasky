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

  
flags.DEFINE_string('model_dir', '/home/gezi/temp/textsum/model.seq2seq.attention/', '')

flags.DEFINE_string('algo', 'seq2seq', 'default algo is bow(cbow), also support rnn, show_and_tell, TODO cnn')

flags.DEFINE_string('vocab', '/home/gezi/temp/textsum/tfrecord/seq-basic.10w/train/vocab.txt', 'vocabulary file')

import sys, os, math
import gezi, melt
import numpy as np

from deepiu.util import text2ids
from deepiu.image_caption.algos import algos_factory
from deepiu.seq2seq.rnn_decoder import SeqDecodeMethod

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
  init_states = predictor.inference([
                                        'beam_search_beam_size',
                                        'beam_search_initial_state', 
                                        'beam_search_initial_ids', 
                                        'beam_search_initial_logprobs',
                                        'beam_search_initial_alignments',
                                        ], 
                                        feed_dict= {
                                          tf.get_collection('input_text_feed')[0] : [word_ids]
                                        })

  step_func = lambda input_feed, state_feed : predictor.inference([
                                        'beam_search_state', 
                                        'beam_search_ids', 
                                        'beam_search_logprobs',
                                        'attention_alignments', #optional
                                        ], 
                                        feed_dict= {
                                          #TODO...attetion still need input_text feed, see rnn_decoder.py  beam_search_step
                                          #but not hurt perfomance much because encoder is fast? Is it possible to avoid this?
                                          #anyway if no attention  will not need input_text_feed
                                          tf.get_collection('input_text_feed')[0] : [word_ids],
                                          tf.get_collection('beam_search_input_feed')[0] : input_feed,
                                          tf.get_collection('beam_search_state_feed')[0] : state_feed
                                        })

  max_words = FLAGS.decode_max_words if FLAGS.decode_max_words else TEXT_MAX_WORDS
  beams = melt.seq2seq.beam_search(init_states, 
                                   step_func, 
                                   end_id=text2ids.end_id(), 
                                   max_words=max_words, 
                                   length_normalization_factor=0.)

  for i, beam in enumerate(beams):
    print(i, beam.words, text2ids.ids2text(beam.words), math.exp(beam.logprob), beam.logprob, beam.score, beam.logprobs)
    #print(beam.alignments_list)

  print('beam search using time(ms):', timer.elapsed_ms())


def main(_):
  text2ids.init()

  global_scope = ''
  if FLAGS.add_global_scope:
    global_scope = FLAGS.global_scope if FLAGS.global_scope else FLAGS.algo
 
  with tf.variable_scope(global_scope):
    predictor =  algos_factory.gen_predictor(FLAGS.algo)
    with tf.variable_scope(FLAGS.main_scope) as scope:
      beam_text, beam_score = predictor.init_predict_text(decode_method=SeqDecodeMethod.beam_search, 
                                                          beam_size=FLAGS.beam_size,
                                                          convert_unk=False)  

  predictor.load(FLAGS.model_dir) 

  predict(predictor, "ʪĤ��ʪ��")
  predict(predictor, "�����Ȱͺ��ű��ġ����������������ۣ������²ۣ�Ҫ������Ϊ������λ�����һ����")
  predict(predictor, "��Ů١���")
  predict(predictor, "����̫����ô����")
  predict(predictor, "���������һ�Ը�Ů�ڿ�����ջ�͸����˿¶�δ���������ڿ�Ů��-�Ա���")
  predict(predictor, "����������ʵ��С��ô��,����������ʵ��С���δ�ʩ")

  text = raw_input('')
  predict(predictor, text)
  


if __name__ == '__main__':
  tf.app.run()
