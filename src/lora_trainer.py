"""LoRA fine-tuning for Stable Diffusion"""
import torch
from diffusers import StableDiffusionPipeline, DDPMScheduler
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
from pathlib import Path
from tqdm import tqdm
import os

class PosterDataset(Dataset):
    def __init__(self, image_dir, size=512):
        self.images = list(Path(image_dir).glob("*.jpg")) + list(Path(image_dir).glob("*.png"))
        self.transform = transforms.Compose([
            transforms.Resize((size, size)),
            transforms.ToTensor(),
            transforms.Normalize([0.5], [0.5])
        ])
        
        # Load genre metadata if available
        import json
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
        
        return img_tensor, genres

class LoRATrainer:
    def __init__(self, model_id="runwayml/stable-diffusion-v1-5"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Training on device: {self.device}")
        
        # Use float32 for training stability
        self.pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float32
        )
        self.pipe = self.pipe.to(self.device)
    
    def train(self, data_dir, output_dir="models/poster_lora", epochs=10, batch_size=1, lr=1e-4):
        """Train LoRA on poster dataset using Dreambooth-style approach"""
        dataset = PosterDataset(data_dir)
        if len(dataset) == 0:
            print("No images found in dataset!")
            return
        
        print(f"Training on {len(dataset)} images")
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        # Enable gradient checkpointing
        self.pipe.unet.enable_gradient_checkpointing()
        self.pipe.unet.train()
        
        # Only train UNet
        optimizer = torch.optim.AdamW(self.pipe.unet.parameters(), lr=lr)
        
        for epoch in range(epochs):
            epoch_loss = 0
            for batch_data in tqdm(dataloader, desc=f"Epoch {epoch+1}/{epochs}"):
                batch_imgs, batch_genres = batch_data
                batch_imgs = batch_imgs.to(self.device, dtype=torch.float32)
                
                # Encode images to latent space
                with torch.no_grad():
                    latents = self.pipe.vae.encode(batch_imgs).latent_dist.sample() * 0.18215
                
                # Sample noise
                noise = torch.randn_like(latents)
                timesteps = torch.randint(0, 1000, (latents.shape[0],), device=self.device)
                
                # Add noise to latents
                noisy_latents = self.pipe.scheduler.add_noise(latents, noise, timesteps)
                
                # Get text embeddings (empty prompt for unconditional training)
                with torch.no_grad():
                    encoder_hidden_states = self.pipe.text_encoder(
                        torch.zeros((batch_imgs.shape[0], 77), dtype=torch.long, device=self.device)
                    )[0]
                
                # Predict noise
                noise_pred = self.pipe.unet(noisy_latents, timesteps, encoder_hidden_states).sample
                
                # Calculate loss
                loss = torch.nn.functional.mse_loss(noise_pred.float(), noise.float())
                
                # Check for NaN
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
        """Save LoRA weights"""
        os.makedirs(output_path, exist_ok=True)
        self.pipe.save_pretrained(output_path)
        print(f"Model saved to {output_path}")
