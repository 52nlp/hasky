cp ./prepare/bow/flickr/conf.py conf.py
source ./prepare/bow/flickr/config 

dir=/home/gezi/temp/image-caption/ 
model_dir=$dir/model.flickr.rnn.forward
mkdir -p $model_dir
cp ./train-flickr-rnn.sh $model_dir

python ./train.py \
	--train_input=$train_output_path/'train*' \
	--valid_input=$valid_output_path/'test*' \
	--fixed_valid_input=$fixed_valid_output_path/'test*' \
	--valid_resource_dir=$valid_output_path \
	--vocab=$train_output_path/vocab.bin \
  --num_records_file=$train_output_path/num_records.txt \
  --image_url_prefix='D:\data\image-text-sim\flickr\imgs\' \
  --show_eval 1 \
  --metric_eval 1 \
  --metric_eval_interval_steps 1000 \
  --model_dir=$model_dir \
  --show_eval 1 \
  --train_only 0 \
  --save_model 1 \
  --optimizer adagrad \
  --fixed_eval_batch_size 10 \
  --num_fixed_evaluate_examples 3 \
  --num_evaluate_examples 1 \
  --save_interval_seconds 600 \
  --save_interval_steps 1000 \
  --num_negs 1 \
  --debug 0 \
  --feed_dict 0 \
  --algo rnn \
  --interval 100 \
  --eval_interval 1000 \
  --margin 0.5 \
  --learning_rate 0.01 \
  --seg_method en \
  --feed_single 0 \
  --dynamic_batch_length 1 \
  --batch_size 16 \
  --rnn_method 0 \
  --rnn_output_method 0 \
  --emb_dim 256 \
  --hidden_size 1024 \
  --monitor_level 2 \
  --num_gpus 0 \

