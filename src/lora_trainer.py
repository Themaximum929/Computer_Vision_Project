"""LoRA fine-tuning for Stable Diffusion"""
import torch
from diffusers import StableDiffusionPipeline, UNet2DConditionModel
from peft import LoraConfig, get_peft_model, TaskType
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
        prompt = "cinematic poster, " + ", ".join(genres) if genres else "cinematic poster"
        
        return img_tensor, prompt

class LoRATrainer:
    def __init__(self, model_id="runwayml/stable-diffusion-v1-5"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Training on device: {self.device}")
        
        self.pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
        )
        self.pipe = self.pipe.to(self.device)
        
        # Configure LoRA
        lora_config = LoraConfig(
            r=16,
            lora_alpha=32,
            target_modules=["to_k", "to_q", "to_v", "to_out.0"],
            lora_dropout=0.1,
        )
        
        # Apply LoRA to UNet
        self.pipe.unet = get_peft_model(self.pipe.unet, lora_config)
        self.pipe.unet.print_trainable_parameters()
    
    def train(self, data_dir, output_dir="models/poster_lora", epochs=10, batch_size=1, lr=1e-4):
        """Train LoRA adapters on poster dataset"""
        dataset = PosterDataset(data_dir)
        if len(dataset) == 0:
            print("No images found in dataset!")
            return
        
        print(f"Training LoRA on {len(dataset)} images")
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        # Only train LoRA parameters
        self.pipe.unet.train()
        optimizer = torch.optim.AdamW(self.pipe.unet.parameters(), lr=lr)
        
        for epoch in range(epochs):
            epoch_loss = 0
            for batch_data in tqdm(dataloader, desc=f"Epoch {epoch+1}/{epochs}"):
                batch_imgs, batch_prompts = batch_data
                batch_imgs = batch_imgs.to(self.device)
                
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
                
                # Calculate loss
                loss = torch.nn.functional.mse_loss(noise_pred, noise)
                
                if torch.isnan(loss):
                    print("Warning: NaN loss detected, skipping batch")
                    continue
                
                optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.pipe.unet.parameters(), 1.0)
                optimizer.step()
                
                epoch_loss += loss.item()
            
            print(f"Epoch {epoch+1} Loss: {epoch_loss/len(dataloader):.4f}")
        
        self.save(output_dir)
        return self.pipe
    
    def save(self, output_path):
        """Save LoRA adapters"""
        os.makedirs(output_path, exist_ok=True)
        self.pipe.unet.save_pretrained(output_path)
        print(f"LoRA adapters saved to {output_path}")
    
    @classmethod
    def load_lora(cls, base_model_id="runwayml/stable-diffusion-v1-5", lora_path="models/poster_lora"):
        """Load pipeline with LoRA adapters"""
        device = "cuda" if torch.cuda.is_available() else "cpu"
        pipe = StableDiffusionPipeline.from_pretrained(
            base_model_id,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32
        )
        
        # Load LoRA weights
        if os.path.exists(lora_path):
            pipe.unet = UNet2DConditionModel.from_pretrained(lora_path)
        
        return pipe.to(device)
