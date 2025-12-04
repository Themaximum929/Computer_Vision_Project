"""
Layout Generation Pipeline
Takes an image and returns a layout graph
"""

import torch
import numpy as np
from typing import Union, Dict, List, Tuple, Optional
from PIL import Image
import os

from layout_generate.layoutPlanter import LayoutPlanter
from layout_generate.PosterO import PosterO
from sample_select.sampleRanker import SampleRanker
from llm_api_wrapper import LLM, SamplingParams
from utils import set_seed


class LayoutGenerationPipeline:
    """
    Pipeline for generating layout graphs from images.
    
    This pipeline encapsulates the entire layout generation process:
    1. Takes an image and design intent bounding boxes
    2. Uses RAG to find similar examples
    3. Generates layout using LLM
    4. Returns layout graph (cls_elem, box_elem)
    """
    
    def __init__(
        self,
        dataset_info: Dict,
        strategy: Dict = {'structure': 'plain', 'injection': 'top'},
        canvas_size: Tuple[int, int] = (513, 750),
        ext_save_name: Optional[str] = None,
        pool_strategy: str = 'all',
        rank_strategy: str = 'random',
        sample_size: int = 5,
        llm_params: Optional[Dict] = None,
        metric_path: Optional[str] = None,
        filter_dict: Optional[Dict] = None,
        describe_list: Optional[List[str]] = None,
        feature_dir: Optional[str] = None,
        seed: int = 42,
    ):
        """
        Initialize the layout generation pipeline.
        
        Args:
            dataset_info: Dictionary containing:
                - 'dataset_name': Name of the dataset ('pku', 'cgl', or 'pstylish7_*')
                - 'design_intent_bbox_dir': Directory with preprocessed design intent bboxes
                - 'annotation_dir': Directory with annotations
                - 'label_info': Label information dictionary
            strategy: Dictionary with 'structure' and 'injection' keys
                - 'structure': 'plain' or 'hierarchical'
                - 'injection': 'none', 'top', 'pulse', or 'pulse_wh'
            canvas_size: Target canvas size (width, height). Default: (513, 750)
            ext_save_name: Optional suffix for saved files
            pool_strategy: Strategy for pooling samples ('all', 'metric_filter', etc.)
            rank_strategy: Strategy for ranking samples ('random', 'rank_by_label', etc.)
            sample_size: Number of samples to use for RAG
            llm_params: Dictionary of LLM parameters (temperature, max_tokens, etc.)
            metric_path: Path to metric file (required for metric-based strategies)
            filter_dict: Filter dictionary for metric filtering
            describe_list: List of metrics to describe
            feature_dir: Directory with feature files (for rank_by_feature)
            seed: Random seed
        """
        set_seed(seed)
        
        self.dataset_info = dataset_info
        self.strategy = strategy
        self.canvas_size = canvas_size
        
        # Initialize LayoutPlanter
        self.layout_planter = LayoutPlanter(
            strategy=strategy,
            dataset_info=dataset_info,
            ext_save_name=ext_save_name,
            canvas_size=canvas_size
        )
        
        # Create args-like object for SampleRanker
        class Args:
            def __init__(self):
                self.pool_strategy = pool_strategy
                self.rank_strategy = rank_strategy
                self.sample_size = sample_size
                self.metric_path = metric_path or ''
                self.filter_dict = filter_dict or ''
                self.describe_list = describe_list or []
                self.feature_dir = feature_dir or ''
        
        args = Args()
        
        # Initialize SampleRanker
        self.sampler = SampleRanker(
            args, 
            self.layout_planter, 
            pool_strategy, 
            rank_strategy
        )
        
        # Initialize LLM
        llm_params = llm_params or {}
        self.llm = LLM()
        self.sampling_params = SamplingParams(
            temperature=llm_params.get('temperature', 0.7),
            max_tokens=llm_params.get('max_tokens', 800),
            top_p=llm_params.get('top_p', 1.0),
            frequency_penalty=llm_params.get('frequency_penalty', 0.0),
            presence_penalty=llm_params.get('presence_penalty', 0.0),
            n=llm_params.get('num_return', 10),
            stop=llm_params.get('stop_token', ["\n\n"]) if llm_params.get('stop_token') else None,
        )
        
        # Initialize PosterO
        self.posterO = PosterO(self.llm, self.layout_planter, self.sampler)
        
        # Setup prompt dict based on dataset
        self.prompt_dict = self._get_prompt_dict(dataset_info['dataset_name'])
    
    def _get_prompt_dict(self, dataset_name: str) -> Dict:
        """Get prompt dictionary based on dataset name."""
        if dataset_name in ['pku', 'cgl']:
            return {
                'opening': "The following are some scalable vector graphics (svg) allocating elements on the canvas.\n",
                'rag_opening': "Example {}: ",
                'rule': "First, learn from the examples and understand how this template works.\nThen, create a new one while following the rules:\n1. The svg must be meaningful, which implies that empty, all-zero, or symbolic attributes are not allowed.\n2. <rect> is the only legal svg tag, and the inner <rect> must be within the outer <svg>.\n3. The id of <rect> must be unique and picked from {}.\n4. The position of <rect> should be clustered neatly in avaliable areas while avoiding intersection. If intersected, <rect> should be resized or moved.\n",
                'pulse_appendix': ""
            }
        elif dataset_name.startswith('pstylish7') or dataset_name.startswith('ps'):
            return {
                'opening': "The following are some scalable vector graphics (svg) allocating elements on the canvas.\n",
                'rag_opening': "Example {}: ",
                'rule': "First, learn from the examples and understand how this template works.\nThen, create a new one while following the rules:\n1. The svg must be meaningful, which implies that empty, all-zero, or symbolic attributes are not allowed.\n2. <rect>, <ellipse>, and <path> are the only legal svg tag, and the inner tags must be within the outer <svg>.\n3. The id of each tag must be unique and picked from {}.\n4. The position of each tag should be clustered neatly in avaliable areas while avoiding intersection. If intersected, the tags should be resized or moved.\n",
                'pulse_appendix': ""
            }
        else:
            raise ValueError(f'Invalid dataset_name: {dataset_name}')
    
    def _get_image_size(self, image: Union[str, np.ndarray, Image.Image]) -> Tuple[int, int]:
        """Get image size from various input formats."""
        if isinstance(image, str):
            img = Image.open(image)
            return img.size  # (width, height)
        elif isinstance(image, np.ndarray):
            if len(image.shape) == 3:
                return (image.shape[1], image.shape[0])  # (width, height)
            else:
                raise ValueError("Invalid image array shape")
        elif isinstance(image, Image.Image):
            return image.size  # (width, height)
        else:
            raise TypeError(f"Unsupported image type: {type(image)}")
    
    def generate_layout(
        self,
        image: Union[str, np.ndarray, Image.Image],
        design_intent_bboxes: List[Tuple[int, int, int, int]],
        labels: Optional[List] = None,
        num_generations: int = 1,
        label_rback: bool = False,
    ) -> Dict:
        """
        Generate layout graph from an image.
        
        Args:
            image: Input image (path string, numpy array, or PIL Image)
            design_intent_bboxes: List of design intent bounding boxes in format 
                [(x1, y1, x2, y2), ...]
            labels: Optional list of labels to use. If None, randomly selected from training set
            num_generations: Number of layout generations to return
            label_rback: Whether to use label rollback from RAG results
        
        Returns:
            Dictionary containing:
                - 'layout_graphs': List of layout graphs, each with:
                    - 'cls_elem': List of class labels
                    - 'box_elem': List of bounding boxes
                - 'svg_results': List of generated SVG strings
                - 'canvas_size': Canvas size used
        """
        # Get image size
        if isinstance(image, str):
            image_path = image
            canvas_size_orig = self._get_image_size(image)
        else:
            image_path = None
            canvas_size_orig = self._get_image_size(image)
        
        # Scale design intent bboxes from original image size to target canvas size
        canvas_ratio = (
            self.canvas_size[0] / canvas_size_orig[0],
            self.canvas_size[1] / canvas_size_orig[1]
        )
        
        scaled_bboxes = [
            (
                int(bbox[0] * canvas_ratio[0]),
                int(bbox[1] * canvas_ratio[1]),
                int(bbox[2] * canvas_ratio[0]),
                int(bbox[3] * canvas_ratio[1])
            )
            for bbox in design_intent_bboxes
        ]
        
        # Create instance dictionary (similar to db_test entries)
        # The instance should have the target canvas_size for getSVGPrompt
        instance = {
            'poster_path': image_path or 'input_image',
            'canvas_size': self.canvas_size,  # Target canvas size
            'den_box': scaled_bboxes,
            'dataset': self.dataset_info['dataset_name']
        }
        
        # Get labels (either provided or random from training set)
        if labels is None:
            db_size = len(self.layout_planter.db_train)
            labels = self.layout_planter.db_train[np.random.randint(db_size)]['layout']['cls_elem']
        
        # Get RAG results
        rag_kwargs = {
            'instance': instance,
            'labels': labels,
            'split_name': 'test',
            'self_i': 0
        }
        rag_results = self.sampler(**rag_kwargs)
        
        # Handle label rollback if requested
        if label_rback:
            labels = self.layout_planter.intepreter(rag_results['layout_description'][0][1])['cls_elem']
        
        # Build prompt
        rag = "\n".join([
            self.prompt_dict['rag_opening'].format(j) + head + svg 
            for j, (head, svg) in enumerate(rag_results['layout_description'])
        ])
        
        pulse = self.layout_planter.getSVGPrompt(
            labels, 
            self.dataset_info['label_info'], 
            instance
        ) + self.prompt_dict['pulse_appendix']
        
        # Format labels for the rule prompt
        if isinstance(labels[0], str):
            label_str = ', '.join(labels)
        else:
            label_str = ', '.join([self.dataset_info['label_info'][l]['type'] for l in labels])
        
        prompt = "\n".join([
            self.prompt_dict['opening'],
            rag,
            self.prompt_dict['rule'].format(label_str),
            pulse
        ])
        
        # Generate layouts
        svg_results = []
        interpret_results = []
        
        while len(interpret_results) < num_generations:
            outputs = self.llm.generate(prompt, sampling_params=self.sampling_params)[0].outputs
            
            for output in outputs:
                try:
                    interpret = self.layout_planter.intepreter(output.text)
                    svg_results.append(output.text)
                    interpret_results.append(interpret)
                except Exception as e:
                    print(f"Failed to interpret SVG: {e}")
                    continue
                
                if len(interpret_results) >= num_generations:
                    break
        
        return {
            'layout_graphs': interpret_results[:num_generations],
            'svg_results': svg_results[:num_generations],
            'canvas_size': self.canvas_size,
            'labels': labels,
            'design_intent_bboxes': scaled_bboxes
        }


def create_pipeline_from_args(args) -> LayoutGenerationPipeline:
    """
    Create a pipeline from parsed arguments (from get_args_infer_dataset).
    
    Args:
        args: Parsed arguments from get_args_infer_dataset()
    
    Returns:
        LayoutGenerationPipeline instance
    """
    llm_params = {
        'temperature': args.temperature,
        'max_tokens': args.max_tokens,
        'top_p': args.top_p,
        'frequency_penalty': args.frequency_penalty,
        'presence_penalty': args.presence_penalty,
        'num_return': args.num_return,
        'stop_token': args.stop_token,
    }
    
    filter_dict = None
    if args.pool_strategy.startswith('metric') and hasattr(args, 'filter_dict'):
        filter_dict = args.filter_dict
    
    pipeline = LayoutGenerationPipeline(
        dataset_info=args.dataset_info,
        strategy={'structure': args.structure[0], 'injection': args.injection[0]} if args.structure and args.injection else {'structure': 'plain', 'injection': 'top'},
        canvas_size=args.canvas_size,
        ext_save_name=args.ext_save_name,
        pool_strategy=args.pool_strategy,
        rank_strategy=args.rank_strategy,
        sample_size=args.sample_size,
        llm_params=llm_params,
        metric_path=args.metric_path if hasattr(args, 'metric_path') else None,
        filter_dict=filter_dict,
        describe_list=args.describe_list if hasattr(args, 'describe_list') else None,
        feature_dir=args.feature_dir if hasattr(args, 'feature_dir') else None,
    )
    
    return pipeline


# Example usage:
if __name__ == '__main__':
    """
    Example usage of the layout generation pipeline:
    
    # 1. Setup dataset info
    dataset_info = {
        'dataset_name': 'pstylish7_movie-poster',
        'design_intent_bbox_dir': '/path/to/design_intent_bbox_dir',
        'annotation_dir': '/path/to/annotation_dir',
        'label_info': {
            'T-G': {'type': 'text-general', 'color': 'green'},
            'L': {'type': 'logo', 'color': 'red'},
            'U': {'type': 'underlay', 'color': 'orange'},
            # ... other labels
        }
    }
    
    # 2. Create pipeline
    pipeline = LayoutGenerationPipeline(
        dataset_info=dataset_info,
        strategy={'structure': 'plain', 'injection': 'top'},
        canvas_size=(513, 750),
        sample_size=5,
        rank_strategy='random'
    )
    
    # 3. Generate layout from image
    image_path = '/path/to/image.jpg'
    design_intent_bboxes = [(100, 100, 400, 300), (50, 500, 450, 700)]  # Example bboxes
    
    result = pipeline.generate_layout(
        image=image_path,
        design_intent_bboxes=design_intent_bboxes,
        num_generations=1
    )
    
    # 4. Access results
    layout_graph = result['layout_graphs'][0]
    print(f"Classes: {layout_graph['cls_elem']}")
    print(f"Boxes: {layout_graph['box_elem']}")
    """
    pass
