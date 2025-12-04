#!/bin/bash
# Run PosterO Generalized Layout Generation

# Configuration
GPU_ID=0
MISTRAL_PATH="/home/themaximum/models/mistral-7b-instruct"
EXP_NAME="key2poster_exp1"
POSTERO_DIR="/home/themaximum/Documents/GitHub/PosterO-CVPR2025"
DATASET_ROOT="/home/themaximum/Documents/GitHub/Computer_Vision_Project"

# Setup environment
export DATASET_ROOT=$DATASET_ROOT
export CUDA_VISIBLE_DEVICES=$GPU_ID

cd $POSTERO_DIR/generalized_setting

# Run inference for all 7 categories
echo "Running PosterO Generalized Layout Generation..."
echo "Dataset: $DATASET_ROOT/PStylish7"
echo "Model: $MISTRAL_PATH"
echo "Experiment: $EXP_NAME"

for i in $(seq 0 6); do
    echo ""
    echo "Processing category $i/6..."
    python main.py \
        --dataset_name "ps" \
        --ps_group $i \
        --ps_dm_name "predm_zs" \
        --canvas_size_w 513 \
        --canvas_size_h 0 \
        --structure "plain" \
        --injection "top" \
        --design_intent_bbox_dir "${DATASET_ROOT}/PStylish7" \
        --annotation_dir "${DATASET_ROOT}/PStylish7" \
        --model_dir $MISTRAL_PATH \
        --rank_strategy "rank_by_feature" \
        --N 1 \
        --num_return 1 \
        --label_rback \
        --sample_size 10 \
        --exp_name $EXP_NAME
done

echo ""
echo "✓ Inference complete!"
echo "Results saved to: $POSTERO_DIR/generalized_setting/$(basename $MISTRAL_PATH)/"

# Evaluate results
echo ""
echo "Running evaluation..."
source eval.sh "$(basename $MISTRAL_PATH)/{}/plain_top_predm_zs_${EXP_NAME}_1.pt"

echo ""
echo "✓ Done! Check results in $POSTERO_DIR/generalized_setting/"
