"""PosterO Generalized with HuggingFace API (no local GPU needed)"""
import sys
import os
sys.path.append('/home/themaximum/Documents/GitHub/PosterO-CVPR2025/generalized_setting')

import torch
import numpy as np
from layout_generate.layoutPlanter import LayoutPlanter
from sample_select.sampleRanker import SampleRanker
import requests
import time

class PosterOGeneralizedAPI:
    """Use HuggingFace Inference API instead of local model"""
    
    CATEGORIES = {
        'chinese-poem': 'Cultural education',
        'food-menu': 'Merchandising display',
        'kind-animals': 'Public advocacy',
        'london-subway': 'Public safety',
        'motivational-quote': 'Social media',
        'movie-poster': 'Entertainment marketing',
        'travel-vintage': 'Artwork exhibition'
    }
    
    LABEL_INFO = {
        'T-G': {'type': 'text-general', 'color': 'green'}, 
        'T-V': {'type': 'text-vertical', 'color': 'green'},
        'T-R': {'type': 'text-rotated', 'color': 'green'},
        'T-S': {'type': 'text-ellipse', 'color': 'green'},
        'T-C': {'type': 'text-curved', 'color': 'green'},
        'L': {'type': 'logo', 'color': 'red'},
        'U': {'type': 'underlay', 'color': 'orange'},
        'E': {'type': 'embellishment', 'color': 'blue'}
    }
    
    def __init__(self, hf_token, dataset_root, canvas_size=(513, 0), model="mistralai/Mistral-7B-Instruct-v0.2"):
        """
        Args:
            hf_token: HuggingFace API token
            dataset_root: Path to PStylish7 dataset
            canvas_size: (width, height)
            model: HuggingFace model ID
        """
        self.hf_token = hf_token
        self.dataset_root = dataset_root
        self.canvas_size = canvas_size
        self.model = model

    
    def _call_api(self, prompt, max_retries=3):
        """Call HuggingFace Inference API"""
        from huggingface_hub import InferenceClient
        client = InferenceClient(token=self.hf_token)
        
        try:
            result = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                max_tokens=800,
                temperature=0.7
            )
            return result.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"HF API error: {e}")

    
    def generate_layout(self, category, num_elements=3, sample_size=10, seed=42):
        """Generate layout using HuggingFace API"""
        if category not in self.CATEGORIES:
            raise ValueError(f"Category must be one of {list(self.CATEGORIES.keys())}")
        
        np.random.seed(seed)
        torch.manual_seed(seed)
        
        category_path = os.path.join(self.dataset_root, category)
        design_intent_path = os.path.join(category_path, 'predm_zs')
        
        dataset_info = {
            'dataset_name': f'pstylish7_{category}',
            'design_intent_bbox_dir': design_intent_path,
            'annotation_dir': category_path,
            'label_info': self.LABEL_INFO
        }
        
        strategy = {'structure': 'plain', 'injection': 'top'}
        layout_planter = LayoutPlanter(strategy, dataset_info=dataset_info, canvas_size=self.canvas_size)
        
        class Args:
            pool_strategy = 'all'
            rank_strategy = 'rank_by_feature'
            feature_dir = os.path.join(design_intent_path, 'features')
            metric_path = ''
            filter_dict = {}
        
        Args.sample_size = sample_size
        
        sampler = SampleRanker(Args(), layout_planter, Args.pool_strategy, Args.rank_strategy)
        
        test_instance = layout_planter.db_test[0]
        labels = layout_planter.db_train[0]['layout']['cls_elem'][:num_elements]
        
        rag_kwargs = {'instance': test_instance, 'labels': labels, 'split_name': 'test', 'self_i': 0}
        rag_results = sampler(**rag_kwargs)
        
        prompt_dict = {
            'opening': "The following are some scalable vector graphics (svg) allocating elements on the canvas.\n",
            'rag_opening': "Example {}: ",
            'rule': f"First, learn from the examples and understand how this template works.\nThen, create a new one while following the rules:\n1. The svg must be meaningful, which implies that empty, all-zero, or symbolic attributes are not allowed.\n2. <rect>, <ellipse>, and <path> are the only legal svg tag, and the inner tags must be within the outer <svg>.\n3. The id of each tag must be unique and picked from {labels}.\n4. The position of each tag should be clustered neatly in avaliable areas while avoiding intersection. If intersected, the tags should be resized or moved.\n",
            'pulse_appendix': ""
        }
        
        rag = "\n".join([prompt_dict['rag_opening'].format(j) + head + svg for j, (head, svg) in enumerate(rag_results['layout_description'])])
        pulse = layout_planter.getSVGPrompt(labels, self.LABEL_INFO, test_instance)
        prompt = "\n".join([prompt_dict['opening'], rag, prompt_dict['rule'], pulse])
        
        # Call API
        output_text = self._call_api(prompt)
        
        # Parse output - extract SVG from response
        svg_text = output_text
        if '<svg' in output_text:
            svg_start = output_text.find('<svg')
            svg_end = output_text.find('</svg>') + 6
            svg_text = output_text[svg_start:svg_end]
        
        try:
            layout = layout_planter.intepreter(svg_text)
            return {
                'bboxes': layout.get('bbox_elem', []),
                'labels': layout.get('cls_elem', []),
                'canvas_size': layout.get('canvas_size', self.canvas_size),
                'svg': svg_text,
                'category': category
            }
        except Exception as e:
            raise RuntimeError(f"Failed to parse layout: {e}\nSVG: {svg_text[:300]}...")
