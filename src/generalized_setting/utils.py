import torch
import random
import numpy as np
import argparse
import os
import json
import time

def set_seed(seed=42, use_gpu=True, rank=0):
    seed = seed + rank
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if use_gpu:
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)

def get_args_infer_dataset():
    parser = argparse.ArgumentParser()

    # dataset
    # Optional: Dataset name to use. Choices: 'pku', 'cgl', or 'ps' (P-Stylish7)
    parser.add_argument("--dataset_name", default='ps', type=str, choices=['pku', 'cgl', 'ps'],
                        help="Dataset name to use. Choices: 'pku', 'cgl', or 'ps' (P-Stylish7). Default: 'ps'")
    
    # Optional: P-Stylish7 group index (0-6). Required when dataset_name='ps'
    parser.add_argument("--ps_group", default=-1, type=int,
                        help="P-Stylish7 group index (0-6). Required when dataset_name='ps'. Maps to categories: chinese-poem, food-menu, kind-animals, london-subway, motivational-quote, movie-poster, travel-vintage")
    
    # Optional: P-Stylish7 design method name. Required when dataset_name='ps'
    parser.add_argument("--ps_dm_name", default="", type=str,
                        help="P-Stylish7 design method name. Required when dataset_name='ps'. Used to construct the design_intent_bbox_dir path")
    
    # Required: Directory containing design intent bounding box files
    parser.add_argument("--design_intent_bbox_dir", type=str, required=True,
                        help="Directory containing design intent bounding box files. For 'ps' dataset, this will be joined with category and ps_dm_name")
    
    # Required: Directory containing annotation files
    parser.add_argument("--annotation_dir", type=str, required=True,
                        help="Directory containing annotation files. For 'ps' dataset, this will be joined with category")
    
    # Optional: Additional suffix for saved files
    parser.add_argument("--ext_save_name", type=str, default='',
                        help="Additional suffix for saved files. If empty, will be set to None. Default: ''")
    
    # Optional: Canvas width in pixels
    parser.add_argument("--canvas_size_w", type=int, default=513,
                        help="Canvas width in pixels. Default: 513")
    
    # Optional: Canvas height in pixels
    parser.add_argument("--canvas_size_h", type=int, default=750,
                        help="Canvas height in pixels. Default: 750")
    
    # Optional: Structure parameters (variable number of arguments)
    parser.add_argument("--structure", type=str, nargs='*',
                        help="Structure parameters. Accepts multiple space-separated values")
    
    # Optional: Injection parameters (variable number of arguments)
    parser.add_argument("--injection", type=str, nargs='*',
                        help="Injection parameters. Accepts multiple space-separated values")
    
    # hyperpm
    # Optional: Experiment name. If empty, will be auto-generated with timestamp
    parser.add_argument("--exp_name", default='', type=str,
                        help="Experiment name. If empty, will be auto-generated with timestamp. For 'ps' dataset, will be prefixed with ps_dm_name")
    
    # Optional: Number of samples or iterations
    parser.add_argument("--N", default=1, type=int,
                        help="Number of samples or iterations. Will be appended to exp_name. Default: 1")

    # divs split model
    # parser.add_argument("--model_divs_ckpt", default='', type=str)

    # large language model
    # Optional: Model directory for vLLM
    parser.add_argument("--model_dir", default='', type=str, help="Model directory (for vLLM)")
    
    # Optional: Temperature for LLM sampling (controls randomness)
    parser.add_argument("--temperature", default=0.7, type=float,
                        help="Temperature for LLM sampling (controls randomness). Higher values = more random. Default: 0.7")
    
    # Optional: Maximum number of tokens to generate
    parser.add_argument("--max_tokens", default=800, type=int,
                        help="Maximum number of tokens to generate in LLM response. Default: 800")
    
    # Optional: Top-p (nucleus) sampling parameter
    parser.add_argument("--top_p", default=1.0, type=float,
                        help="Top-p (nucleus) sampling parameter for LLM. Controls diversity via cumulative probability. Default: 1.0")
    
    # Optional: Frequency penalty to reduce repetition
    parser.add_argument("--frequency_penalty", default=0.0, type=float,
                        help="Frequency penalty for LLM (reduces repetition of tokens). Default: 0.0")
    
    # Optional: Presence penalty to encourage new topics
    parser.add_argument("--presence_penalty", default=0.0, type=float,
                        help="Presence penalty for LLM (encourages new topics). Default: 0.0")
    
    # Optional: Number of sequences to return from LLM
    parser.add_argument("--num_return", default=10, type=int,
                        help="Number of sequences to return from LLM. Default: 10")
    
    # Optional: Stop token(s) for LLM generation
    parser.add_argument("--stop_token", default="\n\n", type=str,
                        help="Stop token(s) for LLM generation. Generation stops when this token is encountered. Default: '\\n\\n'")
    
    # sample & ranker
    # Optional: Strategy for pooling samples. Required when using metric-based strategies
    parser.add_argument("--pool_strategy", default='all', type=str, choices=['all', 'metric_filter', 'metric_describe', 'metric_filter_describe', 'metric_cluster'],
                        help="Strategy for pooling samples. Choices: 'all' (use all), 'metric_filter' (filter by metrics), 'metric_describe' (describe with metrics), 'metric_filter_describe' (both), 'metric_cluster' (cluster by metrics). Default: 'all'")
    
    # Optional: Strategy for ranking samples
    parser.add_argument("--rank_strategy", default='random', type=str, choices=['random', 'rank_by_label', 'rank_by_denbox', 'rank_by_feature'],
                        help="Strategy for ranking samples. Choices: 'random' (random order), 'rank_by_label' (by label), 'rank_by_denbox' (by density box), 'rank_by_feature' (by features). Default: 'random'")
    
    # Required: Number of samples to select
    parser.add_argument("--sample_size", required=True, type=int,
                        help="Number of samples to select from the pool. Required argument")
    
    # Optional: Path to metric file. Required when pool_strategy starts with 'metric'
    parser.add_argument("--metric_path", default='', type=str,
                        help="Path to metric file. Required when pool_strategy starts with 'metric'")
    
    # Optional: Path to filter dictionary JSON file. Required when pool_strategy starts with 'metric'
    parser.add_argument("--filter_dict", default='', type=str,
                        help="Path to filter dictionary JSON file. Required when pool_strategy starts with 'metric'. Must contain 'dataset' and 'metric' keys")
    
    # Optional: List of metrics to describe. Required when pool_strategy ends with 'describe'
    parser.add_argument("--describe_list", default='', type=str, nargs='*', choices=['ove', 'ali', 'und_l', 'und_s', 'uti', 'occ', 'rea', 'cov', 'con'],
                        help="List of metrics to describe. Required when pool_strategy ends with 'describe'. Choices: 'ove' (overlap), 'ali' (alignment), 'und_l' (underlay large), 'und_s' (underlay small), 'uti' (utility), 'occ' (occlusion), 'rea' (readability), 'cov' (coverage), 'con' (contrast)")
    
    # Optional: Directory containing feature files. Required when rank_strategy='rank_by_feature'
    parser.add_argument("--feature_dir", default='', type=str,
                        help="Directory containing feature files. Required when rank_strategy='rank_by_feature'. For 'ps' dataset, defaults to design_intent_bbox_dir/features if empty")
    
    # Optional: Enable label rollback functionality
    parser.add_argument("--label_rback", action='store_true',
                        help="Enable label rollback functionality")
    
    # bool
    # Optional: Enable visualization preview
    parser.add_argument("--vis_preview", action='store_true',
                        help="Enable visualization preview of results")
    
    # Optional: Enable debug mode
    parser.add_argument("--debug", action='store_true',
                        help="Enable debug mode for additional logging/output")

    args = parser.parse_args()
    
    if args.dataset_name == 'pku':
        label_info = {
            1: {'type': 'text', 'color': 'green'}, 
            2: {'type': 'logo', 'color': 'red'},
            3: {'type': 'underlay', 'color': 'orange'}
        }
    elif args.dataset_name == 'cgl':
        label_info = {
            1: {'type': 'logo', 'color': 'red'},
            2: {'type': 'text', 'color': 'green'},
            3: {'type': 'underlay', 'color': 'orange'},
            4: {'type': 'embellishment', 'color': 'blue'}
        }
    elif args.dataset_name == 'ps':
        assert 0 <= args.ps_group < 7, "`ps_group` must be an integer in [0, 7)."
        assert args.ps_dm_name, "`ps_dm_name` must be provided."
        stylish_category = ['chinese-poem', 'food-menu', 'kind-animals', 'london-subway', 'motivational-quote', 'movie-poster', 'travel-vintage']
        category = stylish_category[args.ps_group]
        args.dataset_name = f'pstylish7_{category}'
        args.design_intent_bbox_dir = os.path.join(args.design_intent_bbox_dir, category, args.ps_dm_name)
        args.annotation_dir = os.path.join(args.annotation_dir, category)
        if args.rank_strategy == 'rank_by_feature':
            if args.feature_dir == '':
                args.feature_dir = os.path.join(args.design_intent_bbox_dir, 'features')
        
        label_info = {
            'T-G': {'type': 'text-general', 'color': 'green'}, 
            'T-V': {'type': 'text-vertical', 'color': 'green'},
            'T-R': {'type': 'text-rotated', 'color': 'green'},
            'T-S': {'type': 'text-ellipse', 'color': 'green'},
            'T-C': {'type': 'text-curved', 'color': 'green'},
            'L': {'type': 'logo', 'color': 'red'},
            'U': {'type': 'underlay', 'color': 'orange'},
            'E': {'type': 'embellishment', 'color': 'blue'}
        }
        
    args.dataset_info = {
        'dataset_name': args.dataset_name,
        'design_intent_bbox_dir': args.design_intent_bbox_dir,
        'annotation_dir': args.annotation_dir,
        'label_info': label_info
    }
    
    if args.ext_save_name == '':
        args.ext_save_name = None
    args.canvas_size = (args.canvas_size_w, args.canvas_size_h)
    
    # dealing sampleRanker
    if args.pool_strategy.startswith('metric'):
        assert args.metric_path != '', "Please provide metric_path."
        assert args.filter_dict != '', "Please provide filter_dict."
        if args.pool_strategy.endswith('describe'):
            assert args.describe_list != '', "Please provide describe_list."

        with open(args.filter_dict, 'r') as f:
            filter_dict = json.load(f)
        assert filter_dict['dataset'] == args.dataset_name, f"provided filter_dict is not compatible to {args.dataset_name}."
        args.filter_dict = filter_dict['metric']
        
    if args.rank_strategy == 'rank_by_feature':
        assert args.feature_dir != '', "Please run extrach.sh first and provide feature_dir."
    
    if args.exp_name == '':
        args.exp_name = time.strftime('%Y-%m-%d_%H-%M-%S')
    else:
        if args.dataset_name.startswith('ps') and args.ps_dm_name:
            args.exp_name = f"{args.ps_dm_name}_{args.exp_name}_{args.N}"
        else:
            args.exp_name = f"{args.exp_name}_{args.N}"
    
    save_dir = os.path.join(os.path.split(args.model_dir)[-1], args.dataset_name)
    os.makedirs(save_dir, exist_ok=True)
    args.save_path = os.path.join(save_dir, f"{{}}_{{}}_{args.exp_name}.pt")
    
    return args