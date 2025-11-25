"""Extract PSD Template Information"""
from psd_tools import PSDImage
import json

def extract_template_info(psd_path):
    """Extract layer information from PSD"""
    psd = PSDImage.open(psd_path)
    
    template_info = {
        "size": {"width": psd.width, "height": psd.height},
        "layers": []
    }
    
    print(f"📄 PSD: {psd_path}")
    print(f"📐 Size: {psd.width}x{psd.height}")
    print(f"\n🎨 Layers:")
    
    for layer in psd:
        layer_info = {
            "name": layer.name,
            "type": layer.kind,
            "visible": layer.visible,
            "bbox": layer.bbox if hasattr(layer, 'bbox') else None
        }
        
        # Extract text layer info
        if layer.kind == 'type':
            try:
                text_data = layer.text
                layer_info["text"] = {
                    "content": str(layer.text),
                    "font": layer.engine_dict.get('Editor', {}).get('Text', {}).get('Font', 'Unknown'),
                    "size": layer.engine_dict.get('Editor', {}).get('Text', {}).get('FontSize', 0),
                    "color": layer.engine_dict.get('Editor', {}).get('Text', {}).get('FillColor', {}),
                }
            except:
                layer_info["text"] = {"content": "Unable to extract"}
        
        template_info["layers"].append(layer_info)
        
        # Print layer info
        print(f"\n  Layer: {layer.name}")
        print(f"    Type: {layer.kind}")
        print(f"    Visible: {layer.visible}")
        if layer.bbox:
            print(f"    Position: {layer.bbox}")
        if "text" in layer_info:
            print(f"    Text: {layer_info['text']}")
    
    # Save to JSON
    output_path = psd_path.replace('.psd', '_info.json')
    with open(output_path, 'w') as f:
        json.dump(template_info, f, indent=2)
    
    print(f"\n✅ Saved to: {output_path}")
    return template_info

if __name__ == "__main__":
    extract_template_info("templates/template1.psd")
