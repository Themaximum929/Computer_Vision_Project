"""LoRA fine-tuning for Stable Diffusion"""
import torch
from diffusers import StableDiffusionPipeline
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
from pathlib import Path
from tqdm import tqdm
import os
import json

class PosterDataset(Dataset):
    def __init__(self, image_dir, size=512):
        self.images = list(Path(image_dir).glob("*.jpg")) + list(Path(image_dir).glob("*.png"))
        self.transform = transforms.Compose([
            transforms.Resize((size, size)),
            transforms.ToTensor(),
            transforms.Normalize([0.5], [0.5])
        ])
        
        # Load genre metadata if available
        metadata_path = Path(image_dir) / "metadata.json"
        self.metadata = {}
        if metadata_path.exists():
            with open(metadata_path) as f:
                data = json.load(f)
                for item in data:
                    self.metadata[Path(item['path']).name] = item['genres']
    
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        img = Image.open(self.images[idx]).convert("RGB")
        img_tensor = self.transform(img)
        
        # Get genre tags for this image
        filename = self.images[idx].name
        genres = self.metadata.get(filename, [])
        # Natural poster prompt - avoid SD keywords
        prompt = "movie poster, " + ", ".join(genres) if genres else "movie poster"
        
        return img_tensor, prompt

class LoRATrainer:
    def __init__(self, model_id="runwayml/stable-diffusion-v1-5", lora_rank=4):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"CUDA available: {torch.cuda.is_available()}")
        print(f"Training on device: {self.device}")
        
        # Use float32 for training stability
        self.pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float32
        ).to(self.device)
        
        # Freeze all parameters
        self.pipe.unet.requires_grad_(False)
        self.pipe.text_encoder.requires_grad_(False)
        self.pipe.vae.requires_grad_(False)
        
        # Unfreeze more layers for stronger style adaptation
        for name, param in self.pipe.unet.named_parameters():
            # Cross-attention (content) + Self-attention (style) + Conv layers (color/texture)
            if "attn2" in name or "attn1" in name or "conv_out" in name or "conv_in" in name:
                param.requires_grad = True
    
    def train(self, data_dir, output_dir="models/poster_lora", epochs=10, batch_size=1, lr=1e-4):
        """Train LoRA adapters on poster dataset"""
        dataset = PosterDataset(data_dir)
        if len(dataset) == 0:
            print("No images found in dataset!")
            return
        
        print(f"Training LoRA on {len(dataset)} images")
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        # Train only unfrozen parameters
        self.pipe.unet.train()
        trainable_params = [p for p in self.pipe.unet.parameters() if p.requires_grad]
        total_params = sum(p.numel() for p in self.pipe.unet.parameters())
        trainable_count = sum(p.numel() for p in trainable_params)
        print(f"Trainable: {trainable_count:,} / {total_params:,} ({100*trainable_count/total_params:.2f}%)")
        optimizer = torch.optim.AdamW(trainable_params, lr=lr)
        
        for epoch in range(epochs):
            epoch_loss = 0
            for batch_data in tqdm(dataloader, desc=f"Epoch {epoch+1}/{epochs}"):
                batch_imgs, batch_prompts = batch_data
                batch_imgs = batch_imgs.to(self.device, dtype=self.pipe.vae.dtype)
                
                # Encode images to latent space
                with torch.no_grad():
                    latents = self.pipe.vae.encode(batch_imgs).latent_dist.sample() * 0.18215
                
                # Sample noise and timesteps
                noise = torch.randn_like(latents)
                timesteps = torch.randint(0, 1000, (latents.shape[0],), device=self.device)
                noisy_latents = self.pipe.scheduler.add_noise(latents, noise, timesteps)
                
                # Get text embeddings
                with torch.no_grad():
                    text_inputs = self.pipe.tokenizer(
                        batch_prompts, padding="max_length", max_length=77, 
                        truncation=True, return_tensors="pt"
                    ).to(self.device)
                    encoder_hidden_states = self.pipe.text_encoder(text_inputs.input_ids)[0]
                
                # Predict noise with LoRA-enhanced UNet
                noise_pred = self.pipe.unet(noisy_latents, timesteps, encoder_hidden_states).sample
                
                # Calculate loss with float32
                loss = torch.nn.functional.mse_loss(noise_pred.float(), noise.float(), reduction="mean")
                
                if torch.isnan(loss):
                    print("Warning: NaN loss detected, skipping batch")
                    continue
                
                optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(trainable_params, 1.0)
                optimizer.step()
                
                epoch_loss += loss.item()
            
            print(f"Epoch {epoch+1} Loss: {epoch_loss/len(dataloader):.4f}")
        
        self.save(output_dir)
        return self.pipe
    
    def save(self, output_path):
        """Save fine-tuned weights"""
        os.makedirs(output_path, exist_ok=True)
        
        # Save all trained weights
        state_dict = {k: v for k, v in self.pipe.unet.state_dict().items() 
                     if any(x in k for x in ["attn2", "attn1", "conv_out", "conv_in"])}
        torch.save(state_dict, os.path.join(output_path, "lora_weights.pth"))
        print(f"Fine-tuned weights saved to {output_path}")
