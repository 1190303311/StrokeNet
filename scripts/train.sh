#!/bin/bash
LOC='/home/u1190303311'
ROOT="${LOC}/StrokeNet"
DATAROOT="${ROOT}/data/NIST/strokenet_data" # set your data root

DATABIN="${DATAROOT}/bpe/bin"

FAIRSEQ="${ROOT}/fairseq"

nist_zhx_en_2keys() {
    LANG_LIST="${DATABIN}/langs.file"
    LANG_PAIRS="zh-en,zh1-en,zh2-en"
    EVAL_LANG_PAIRS="zh-en,"
    
    # these ratios can be changed if you want to analyse the 
    # model behaviour by varying the amount of training data
    SAMP_MAIN='"main:zh-en":0.0'
    SAMP_TGT='"main:zh1-en":1.0,"main:zh2-en":1.0'
    SAMP_SRC='"main:zh1-en":1.0,"main:zh2-en":1.0'
    
    # virtual-data-size is net amount of training data (all inclusive)
    # that the model trains on. 
    SAMPLE_WEIGHTS="{${SAMP_TGT},${SAMP_MAIN}} --virtual-data-size 82465980"
    # experiment identifier; this becomes a dir in checkpoints and experiments folders
    EXPTNAME="NIST"
    RUN="#0"

    # paths to checkpoints and experiments directories
    CKPT="$ROOT/checkpoints/${EXPTNAME}"
    EXPTDIR="$ROOT/logs/${EXPTNAME}"
    mkdir -p "$EXPTDIR"
    mkdir -p "$CKPT"

    # fairseq arguments
    TASK="translation_multi_simple_epoch_cipher --prime-src zh --prime-tgt en"
    LOSS="label_smoothed_cross_entropy_js --js-alpha 5 --js-warmup 500"
    ARCH="transformer"
    MAX_EPOCH=100
    PATIENCE=25
    MAX_TOK=8000
    UPDATE_FREQ=2
    WANDB="NIST"
}

######## exp config call #########
nist_zhx_en_2keys

######## training begins here ####

echo "${EXPTNAME}"
echo "${ARCH}"
echo "${LOSS}"

echo "Entering training.."
fairseq-train --log-format simple --log-interval 1000 \
    $DATABIN --save-dir ${CKPT} --keep-best-checkpoints 1 \
    --fp16 --fp16-init-scale 64 \
    --lang-dict "${LANG_LIST}" --lang-pairs "${LANG_PAIRS}" --encoder-langtok tgt \
    --task ${TASK} \
    --arch transformer --share-all-embeddings \
    --sampling-weights ${SAMPLE_WEIGHTS} \
    --optimizer adam --adam-betas '(0.9, 0.98)' --clip-norm 0.0 \
    --lr 5e-4 --lr-scheduler inverse_sqrt --warmup-updates 4000 \
    --dropout 0.1 --weight-decay 0.0001 \
    --max-epoch $MAX_EPOCH --patience ${PATIENCE} \
    --keep-last-epochs 5 \
    --criterion ${LOSS} \
    --label-smoothing 0.1 \
    --max-tokens $MAX_TOK --update-freq $UPDATE_FREQ --eval-bleu \
    --eval-lang-pairs ${EVAL_LANG_PAIRS} --validate-interval-updates 10000 \
    --valid-subset valid --ignore-unused-valid-subsets --batch-size-valid 200 \
    --eval-bleu-detok moses --eval-bleu-remove-bpe \
    --eval-bleu-print-samples --wandb-project $WANDB \
    --best-checkpoint-metric bleu --maximize-best-checkpoint-metric \
    --eval-bleu-args '{"beam": 5, "max_len_a": 1.0, "max_len_b": 15}' \
    | tee -a "${EXPTDIR}/train.${RUN}.log"

# --wandb-project ${WANDB}
# usage: bash train_cipherdaug.sh


fairseq-generate $DATABIN --task translation_multi_simple_epoch \
    --lang-tok-style "multilingual" --source-lang zh --target-lang en --encoder-langtok "tgt" \
    --lang-dict ${LANG_LIST} \
    --lang-pairs ${LANG_PAIRS} \
    --path $CKPT/checkpoint_best.pt \
    --batch-size 128 --beam 5 --remove-bpe > $CKPT/predict.hyp

cat $CKPT/predict.all | grep -P "^H" |sort -V |cut -f 3- > $CKPT/predict.hyp
sacrebleu -tok 'none' -s 'none' \
$ROOT/test.zh-en.en \
< $CKPT/predict.hyp > $CKPT/predict.score

echo "Sacrebleu score is saved in $CKPT/predict.score."