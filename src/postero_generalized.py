"""PosterO Generalized Layout Generation Integration"""
import sys
import os
sys.path.append('/home/themaximum/Documents/GitHub/PosterO-CVPR2025/generalized_setting')

import torch
import numpy as np
from layout_generate.layoutPlanter import LayoutPlanter
from layout_generate.PosterO import PosterO
from sample_select.sampleRanker import SampleRanker

class PosterOGeneralized:
    """Wrapper for PosterO Generalized Content-Aware Layout Generation"""
    
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
    
    def __init__(self, llm_path, dataset_root, canvas_size=(513, 0)):
        """
        Args:
            llm_path: Path to Mistral-7B or LLaMA model
            dataset_root: Path to PStylish7 dataset
            canvas_size: (width, height), height=0 for auto
        """
        self.llm_path = llm_path
        self.dataset_root = dataset_root
        self.canvas_size = canvas_size
        self.llm = None
        
    def _load_llm(self):
        """Lazy load LLM"""
        if self.llm is None:
            from vllm import LLM, SamplingParams
            self.llm = LLM(self.llm_path)
            self.sampl = SamplingParams(
                temperature=0.7,
                max_tokens=800,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                n=10,
                stop=["\n\n"]
            )
    
    def generate_layout(self, category, num_elements=3, sample_size=10, seed=42):
        """
        Generate layout for specific category
        
        Args:
            category: One of CATEGORIES keys
            num_elements: Number of layout elements
            sample_size: Number of training samples for RAG
            seed: Random seed
            
        Returns:
            dict: Layout with bboxes and element types
        """
        if category not in self.CATEGORIES:
            raise ValueError(f"Category must be one of {list(self.CATEGORIES.keys())}")
        
        self._load_llm()
        np.random.seed(seed)
        torch.manual_seed(seed)
        
        # Setup paths
        category_path = os.path.join(self.dataset_root, category)
        design_intent_path = os.path.join(category_path, 'predm_zs')
        
        dataset_info = {
            'dataset_name': f'pstylish7_{category}',
            'design_intent_bbox_dir': design_intent_path,
            'annotation_dir': category_path,
            'label_info': self.LABEL_INFO
        }
        
        # Create layout planter
        strategy = {'structure': 'plain', 'injection': 'top'}
        layout_planter = LayoutPlanter(
            strategy, 
            dataset_info=dataset_info,
            canvas_size=self.canvas_size
        )
        
        # Create sampler
        class Args:
            pool_strategy = 'all'
            rank_strategy = 'rank_by_feature'
            sample_size = sample_size
            feature_dir = os.path.join(design_intent_path, 'features')
            metric_path = ''
            filter_dict = {}
            
        sampler = SampleRanker(Args(), layout_planter, Args.pool_strategy, Args.rank_strategy)
        
        # Create PosterO
        posterO = PosterO(self.llm, layout_planter, sampler)
        
        # Generate layout
        test_instance = layout_planter.db_test[0]
        labels = layout_planter.db_train[0]['layout']['cls_elem'][:num_elements]
        
        rag_kwargs = {
            'instance': test_instance,
            'labels': labels,
            'split_name': 'test',
            'self_i': 0
        }
        rag_results = sampler(**rag_kwargs)
        
        # Build prompt
        prompt_dict = {
            'opening': "The following are some scalable vector graphics (svg) allocating elements on the canvas.\n",
            'rag_opening': "Example {}: ",
            'rule': f"First, learn from the examples and understand how this template works.\nThen, create a new one while following the rules:\n1. The svg must be meaningful, which implies that empty, all-zero, or symbolic attributes are not allowed.\n2. <rect>, <ellipse>, and <path> are the only legal svg tag, and the inner tags must be within the outer <svg>.\n3. The id of each tag must be unique and picked from {labels}.\n4. The position of each tag should be clustered neatly in avaliable areas while avoiding intersection. If intersected, the tags should be resized or moved.\n",
            'pulse_appendix': ""
        }
        
        rag = "\n".join([
            prompt_dict['rag_opening'].format(j) + head + svg 
            for j, (head, svg) in enumerate(rag_results['layout_description'])
        ])
        
        pulse = layout_planter.getSVGPrompt(labels, self.LABEL_INFO, test_instance)
        prompt = "\n".join([prompt_dict['opening'], rag, prompt_dict['rule'], pulse])
        
        # Generate
        outputs = self.llm.generate(prompt, sampling_params=self.sampl)[0].outputs
        
        for output in outputs:
            try:
                layout = layout_planter.intepreter(output.text)
                return {
                    'bboxes': layout['bbox_elem'],
                    'labels': layout['cls_elem'],
                    'canvas_size': layout['canvas_size'],
                    'svg': output.text,
                    'category': category
                }
            except:
                continue
        
        raise RuntimeError("Failed to generate valid layout")
    
    def batch_generate(self, categories=None, num_elements=3, sample_size=10):
        """Generate layouts for multiple categories"""
        if categories is None:
            categories = list(self.CATEGORIES.keys())
        
        results = {}
        for cat in categories:
            try:
                results[cat] = self.generate_layout(cat, num_elements, sample_size)
            except Exception as e:
                print(f"Failed to generate layout for {cat}: {e}")
                results[cat] = None
        
        return results
