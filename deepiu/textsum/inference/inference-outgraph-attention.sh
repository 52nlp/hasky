source ./prepare/config

python ./inference/inference-outgraph-attention.py \
      --model_dir /home/gezi/new/temp/textsum/model.seq2seq.attention/ \
      --seg_method $online_seg_method \
      --feed_single $feed_single 
