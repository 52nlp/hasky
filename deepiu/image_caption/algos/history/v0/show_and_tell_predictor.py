#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==============================================================================
#          \file   show_and_tell_predictor.py
#        \author   chenghuige  
#          \date   2016-09-04 17:50:21.017234
#   \Description  
# ==============================================================================

  
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
flags = tf.app.flags
FLAGS = flags.FLAGS


import numpy as np

import melt
import conf 
from conf import IMAGE_FEATURE_LEN, TEXT_MAX_WORDS

import vocabulary

import text2ids 
from text2ids import idslist2texts

import gezi

import algo.show_and_tell
ShowAndTell = algo.show_and_tell.ShowAndTell


class ShowAndTellPredictor(ShowAndTell, melt.PredictorBase):
  def __init__(self):
    super(ShowAndTellPredictor, self).__init__()

  def init_predict_texts(self):
    self.image_feature_place = tf.placeholder(tf.float32, [IMAGE_FEATURE_LEN], name='image')
    self.texts = self.build_predict_texts_graph(self.image_feature_place)

  def predict_texts(self, images):
    feed_dict = {
      self.image_feature_place: images,
      }
    generated_words = self.sess.run(self.texts, feed_dict)
    vocab = vocabulary.get_vocab()
    texts = idslist2texts(generated_words)
    return texts

  def init_predict(self):
    self.image_feature_place = tf.placeholder(tf.float32, [IMAGE_FEATURE_LEN], name='image')
    self.text = tf.placeholder(tf.int32, [TEXT_MAX_WORDS])
    self.loss = self.build_predict_graph(self.image_feature_place, self.text)

  #@TODO all predict means single predict, and use bulk_predict for mulitpe predicts
  def predict(self, image, text):
    feed_dict = {
      self.image_feature_place: image,
      self.text: text,
    }
    loss = self.sess.run(self.loss, feed_dict)
    return loss

  def bulk_predict(self, images, texts):
    scores = []
    for image in images:
      score_list = []
      for text in texts:
        score = self.predict(image, text)
        score_list.append(score)
      scores.append(score_list)
    return np.array(scores)

  def build_predict_texts_graph(self, image):
    batch_size = tf.shape(image)[0]

    image_emb = tf.matmul(image, self.encode_img_W) + self.encode_img_b

    #----@FIXME strange not work here, but work for train... build_main_graph why?
    state = tf.zeros([batch_size, self.lstm.state_size])
    #state = tf.zeros([1, self.lstm.state_size])
    #state = tf.zeros(zeros_dims)
    generated_words = []

    maxlen = 10
    with tf.variable_scope("RNN"):
      output, state = self.lstm(image_emb, state)
      #not work!
      #last_word = tf.nn.embedding_lookup(self.emb, [0] * batch_size) + self.bemb
      last_word = tf.nn.embedding_lookup(self.emb, tf.zeros([batch_size], tf.int32)) + self.bemb

      for i in range(maxlen):
        tf.get_variable_scope().reuse_variables()
        output, state = self.lstm(last_word, state)

        logit_words = tf.matmul(output, self.embed_word_W) + self.embed_word_b

        #argmax will decrease dimension by 1
        max_prob_word = tf.argmax(logit_words, 1)
        #if i == 0:
        #max_prob_word = tf.nn.top_k(logit_words, 2)[1][:,1]
        #top_words = tf.nn.top_k(logit_words, 10)[1]
        #max_prob_word = tf.nn.top_k(logit_words, 5)[1][:, np.random.choice(5, 1)]

        #with tf.device("/cpu:0"):
        last_word = tf.nn.embedding_lookup(self.emb, max_prob_word) + self.bemb
        max_prob_word = tf.reshape(max_prob_word, [batch_size, -1])
        generated_words.append(max_prob_word)
        #generated_words.append(top_words)

      generated_words = tf.concat(1, generated_words)
      return generated_words

  def build_predict_graph(self, image, text):
    image = tf.reshape(image, [1, IMAGE_FEATURE_LEN])
    text = tf.reshape(text, [1, TEXT_MAX_WORDS])

    pad = tf.zeros([1,1], dtype=tf.int32)
    text = tf.concat(1, [pad, text, pad])

    mask = tf.zeros_like(text)
    mask = tf.cast(tf.greater(text, mask), tf.float32)

    image_emb = tf.matmul(image, self.encode_img_W) + self.encode_img_b

    state = tf.zeros([1, self.lstm.state_size])

    loss = tf.zeros([1])
    with tf.variable_scope("RNN"):
      for i in range(self.n_lstm_steps): 
        #print i
        if i == 0:
          current_emb = image_emb
        else:
          #with tf.device("/cpu:0"):
          current_emb = tf.nn.embedding_lookup(self.emb, text[:,i-1]) + self.bemb
        if i > 0 : tf.get_variable_scope().reuse_variables()
        output, state = self.lstm(current_emb, state) # (batch_size, dim_hidden)
        
        if i > 0: 
          labels = text[:, i]
          logit_words = tf.matmul(output, self.embed_word_W) + self.embed_word_b 
          cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(logit_words, labels)
          cross_entropy = cross_entropy * mask[:,i]
          loss += cross_entropy

      loss = loss / tf.reduce_sum(mask[:,1:], 1)
      loss = tf.squeeze(loss)
      return loss
