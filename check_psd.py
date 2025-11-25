from psd_tools import PSDImage
import json

psd = PSDImage.open("templates/template1.psd")
print(f"Size: {psd.width}x{psd.height}")
print(f"Total layers: {len(list(psd.descendants()))}")

layers = []
for i, layer in enumerate(psd.descendants()):
    info = {
        "name": layer.name,
        "kind": layer.kind,
        "visible": layer.visible,
        "bbox": list(layer.bbox) if hasattr(layer, 'bbox') else None
    }
    
    if layer.kind == 'type':
        try:
            info["text"] = str(layer.text)
        except:
            info["text"] = "N/A"
    
    layers.append(info)
    try:
        print(f"\n[{i}] {layer.name} ({layer.kind})")
        if info.get("text"):
            print(f"    Text: {info['text']}")
        if info["bbox"]:
            print(f"    Position: {info['bbox']}")
    except:
        print(f"\n[{i}] Layer {i} ({layer.kind})")
        if info["bbox"]:
            print(f"    Position: {info['bbox']}")

with open("templates/template1_layers.json", "w") as f:
    json.dump({"size": [psd.width, psd.height], "layers": layers}, f, indent=2)

print("\nSaved to: templates/template1_layers.json")
